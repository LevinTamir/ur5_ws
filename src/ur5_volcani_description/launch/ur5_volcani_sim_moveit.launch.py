from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def launch_setup(context, *args, **kwargs):
    ur_type = LaunchConfiguration("ur_type")
    safety_limits = LaunchConfiguration("safety_limits")
    controllers_file = LaunchConfiguration("controllers_file")
    description_file = LaunchConfiguration("description_file")
    world_name = LaunchConfiguration("world_name")

    ur_control_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("ur5_volcani_description"), "launch", "ur5_volcani_sim_control.launch.py"]
            )
        ),
        launch_arguments={
            "ur_type": ur_type,
            "safety_limits": safety_limits,
            "controllers_file": controllers_file,
            "description_file": description_file,
            "launch_rviz": "false",
            "world_name": world_name,
        }.items(),
    )

    ur_moveit_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("ur5_volcani_description"), "launch", "ur5_volcani_moveit.launch.py"]
            )
        ),
        launch_arguments={
            "ur_type": ur_type,
            "use_sim_time": "true",
            "launch_rviz": "true",
        }.items(),
    )

    collision_publisher = Node(
        package="ur5_volcani_description",
        executable="publish_collision_objects.py",
        name="collision_object_publisher",
        output="screen",
        parameters=[{"use_sim_time": True}],
    )

    return [ur_control_launch, ur_moveit_launch, collision_publisher]


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
        DeclareLaunchArgument(
            "controllers_file",
            default_value=PathJoinSubstitution(
                [FindPackageShare("ur5_volcani_description"), "config", "ur_controllers.yaml"]
            ),
            description="YAML file with the controllers configuration.",
        )
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
        DeclareLaunchArgument("world_name", default_value="lab",
                              description="World name (without .sdf): empty, lab, or feild.")
    )

    return LaunchDescription(declared_arguments + [OpaqueFunction(function=launch_setup)])
