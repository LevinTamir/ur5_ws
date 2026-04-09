import os
from os import pathsep
from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
    RegisterEventHandler,
    SetEnvironmentVariable,
)
from launch.conditions import IfCondition, UnlessCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
    PythonExpression,
    IfElseSubstitution,
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def launch_setup(context, *args, **kwargs):
    ur_type = LaunchConfiguration("ur_type")
    safety_limits = LaunchConfiguration("safety_limits")
    safety_pos_margin = LaunchConfiguration("safety_pos_margin")
    safety_k_position = LaunchConfiguration("safety_k_position")
    controllers_file = LaunchConfiguration("controllers_file")
    tf_prefix = LaunchConfiguration("tf_prefix")
    activate_joint_controller = LaunchConfiguration("activate_joint_controller")
    initial_joint_controller = LaunchConfiguration("initial_joint_controller")
    description_file = LaunchConfiguration("description_file")
    launch_rviz = LaunchConfiguration("launch_rviz")
    rviz_config_file = LaunchConfiguration("rviz_config_file")
    gazebo_gui = LaunchConfiguration("gazebo_gui")
    world_name = LaunchConfiguration("world_name")

    pkg_share = FindPackageShare("ur5_volcani_description")
    pkg_share_dir = get_package_share_directory("ur5_volcani_description")

    # Build world file path from world_name
    world_file = PathJoinSubstitution([pkg_share, "worlds", PythonExpression(
        ["'", world_name, "'", " + '.sdf'"]
    )])

    # Set GZ_SIM_RESOURCE_PATH: parent of share dir (for package:// URI resolution)
    # plus models dir (for model:// URI resolution in SDF worlds)
    model_path = str(Path(pkg_share_dir).parent.resolve())
    model_path += pathsep + os.path.join(pkg_share_dir, "models")

    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            description_file,
            " ",
            "safety_limits:=", safety_limits,
            " ",
            "safety_pos_margin:=", safety_pos_margin,
            " ",
            "safety_k_position:=", safety_k_position,
            " ",
            "name:=", "ur",
            " ",
            "ur_type:=", ur_type,
            " ",
            "tf_prefix:=", tf_prefix,
            " ",
            "simulation_controllers:=", controllers_file,
        ]
    )
    robot_description = {"robot_description": robot_description_content}

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="both",
        parameters=[{"use_sim_time": True}, robot_description],
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="log",
        arguments=["-d", rviz_config_file],
        condition=IfCondition(launch_rviz),
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
    )

    delay_rviz_after_joint_state_broadcaster_spawner = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[rviz_node],
        ),
        condition=IfCondition(launch_rviz),
    )

    initial_joint_controller_spawner_started = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[initial_joint_controller, "-c", "/controller_manager"],
        condition=IfCondition(activate_joint_controller),
    )
    initial_joint_controller_spawner_stopped = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[initial_joint_controller, "-c", "/controller_manager", "--stopped"],
        condition=UnlessCondition(activate_joint_controller),
    )

    gz_spawn_entity = Node(
        package="ros_gz_sim",
        executable="create",
        output="screen",
        arguments=[
            "-string", robot_description_content,
            "-name", "ur",
            "-allow_renaming", "true",
            "-J", "shoulder_pan_joint", "0.0",
            "-J", "shoulder_lift_joint", "-1.57",
            "-J", "elbow_joint", "1.57",
            "-J", "wrist_1_joint", "-1.57",
            "-J", "wrist_2_joint", "0.0",
            "-J", "wrist_3_joint", "0.0",
        ],
    )

    gz_launch_description = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [FindPackageShare("ros_gz_sim"), "/launch/gz_sim.launch.py"]
        ),
        launch_arguments={
            "gz_args": IfElseSubstitution(
                gazebo_gui,
                if_value=[" -r -v 4 ", world_file],
                else_value=[" -s -r -v 4 ", world_file],
            )
        }.items(),
    )

    gz_sim_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
            "/rgbd_camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo",
            "/rgbd_camera/image@sensor_msgs/msg/Image[gz.msgs.Image",
            "/rgbd_camera/depth_image@sensor_msgs/msg/Image[gz.msgs.Image",
            "/rgbd_camera/depth_image_camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo",
            "/rgbd_camera/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked",
        ],
        remappings=[
            ("/rgbd_camera/image", "/camera/color/image_raw"),
            ("/rgbd_camera/camera_info", "/camera/color/camera_info"),
            ("/rgbd_camera/depth_image", "/camera/aligned_depth_to_color/image_raw"),
            ("/rgbd_camera/depth_image_camera_info", "/camera/aligned_depth_to_color/camera_info"),
            ("/rgbd_camera/points", "/camera/depth/color/points"),
        ],
        output="screen",
    )

    # Set GZ_SIM_RESOURCE_PATH for model discovery
    gz_resource_path = SetEnvironmentVariable(
        "GZ_SIM_RESOURCE_PATH",
        model_path,
    )

    nodes_to_start = [
        gz_resource_path,
        robot_state_publisher_node,
        joint_state_broadcaster_spawner,
        delay_rviz_after_joint_state_broadcaster_spawner,
        initial_joint_controller_spawner_stopped,
        initial_joint_controller_spawner_started,
        gz_spawn_entity,
        gz_launch_description,
        gz_sim_bridge,
    ]

    return nodes_to_start


def generate_launch_description():
    declared_arguments = []

    declared_arguments.append(
        DeclareLaunchArgument(
            "ur_type",
            description="Type/series of used UR robot.",
            choices=["ur3", "ur3e", "ur5", "ur5e", "ur7e", "ur10", "ur10e", "ur12e", "ur16e", "ur15", "ur20", "ur30"],
            default_value="ur5e",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument("safety_limits", default_value="true",
                              description="Enables the safety limits controller if true.")
    )
    declared_arguments.append(
        DeclareLaunchArgument("safety_pos_margin", default_value="0.15",
                              description="The margin to lower and upper limits in the safety controller.")
    )
    declared_arguments.append(
        DeclareLaunchArgument("safety_k_position", default_value="20",
                              description="k-position factor in the safety controller.")
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "controllers_file",
            default_value=PathJoinSubstitution(
                [FindPackageShare("ur5_volcani_description"), "config", "ur_controllers.yaml"]
            ),
            description="YAML file with the controllers configuration.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument("tf_prefix", default_value='""',
                              description="Prefix of the joint names.")
    )
    declared_arguments.append(
        DeclareLaunchArgument("activate_joint_controller", default_value="true",
                              description="Enable headless mode for robot control.")
    )
    declared_arguments.append(
        DeclareLaunchArgument("initial_joint_controller",
                              default_value="scaled_joint_trajectory_controller",
                              description="Robot controller to start.")
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "description_file",
            default_value=PathJoinSubstitution(
                [FindPackageShare("ur5_volcani_description"), "urdf", "ur5_volcani.urdf.xacro"]
            ),
            description="URDF/XACRO description file with the robot.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument("launch_rviz", default_value="true", description="Launch RViz?")
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "rviz_config_file",
            default_value=PathJoinSubstitution(
                [FindPackageShare("ur_description"), "rviz", "view_robot.rviz"]
            ),
            description="RViz config file to use.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument("gazebo_gui", default_value="true", description="Start Gazebo with GUI?")
    )
    declared_arguments.append(
        DeclareLaunchArgument("world_name", default_value="lab",
                              description="World name (without .sdf extension): empty, lab, or feild.")
    )

    return LaunchDescription(declared_arguments + [OpaqueFunction(function=launch_setup)])
