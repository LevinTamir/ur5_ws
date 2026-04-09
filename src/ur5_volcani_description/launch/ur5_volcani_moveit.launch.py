"""Custom MoveIt launch that uses our SRDF with updated home position."""

import os
import subprocess
import yaml

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

from moveit_configs_utils import MoveItConfigsBuilder
from ament_index_python.packages import get_package_share_directory


def load_yaml(package_name, file_path):
    package_path = get_package_share_directory(package_name)
    absolute_file_path = os.path.join(package_path, file_path)
    try:
        with open(absolute_file_path) as file:
            return yaml.safe_load(file)
    except OSError:
        return None


def generate_launch_description():
    launch_rviz = LaunchConfiguration("launch_rviz")
    ur_type = LaunchConfiguration("ur_type")
    use_sim_time = LaunchConfiguration("use_sim_time")

    # Process our custom SRDF xacro with updated home position
    srdf_xacro_path = os.path.join(
        get_package_share_directory("ur5_volcani_description"),
        "srdf", "ur5_volcani.srdf.xacro",
    )
    srdf_content = subprocess.check_output(
        ["xacro", srdf_xacro_path, "name:=ur"],
        text=True,
    )
    robot_description_semantic = {"robot_description_semantic": srdf_content}

    # Build MoveIt config, pointing to our SRDF so MoveItConfigsBuilder doesn't fail
    moveit_config = (
        MoveItConfigsBuilder(robot_name="ur", package_name="ur_moveit_config")
        .robot_description_semantic(file_path=srdf_xacro_path, mappings={"name": "ur"})
        .to_moveit_configs()
    )

    warehouse_ros_config = {
        "warehouse_plugin": "warehouse_ros_sqlite::DatabaseConnection",
        "warehouse_host": os.path.expanduser("~/.ros/warehouse_ros.sqlite"),
    }

    wait_robot_description = Node(
        package="ur_robot_driver",
        executable="wait_for_robot_description",
        output="screen",
    )

    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            moveit_config.to_dict(),
            robot_description_semantic,
            warehouse_ros_config,
            {
                "use_sim_time": use_sim_time,
                "publish_robot_description_semantic": True,
            },
        ],
    )

    rviz_config_file = PathJoinSubstitution(
        [FindPackageShare("ur_moveit_config"), "config", "moveit.rviz"]
    )
    rviz_node = Node(
        package="rviz2",
        condition=IfCondition(launch_rviz),
        executable="rviz2",
        name="rviz2_moveit",
        output="log",
        arguments=["-d", rviz_config_file],
        parameters=[
            moveit_config.robot_description,
            robot_description_semantic,
            moveit_config.robot_description_kinematics,
            moveit_config.planning_pipelines,
            moveit_config.joint_limits,
            warehouse_ros_config,
            {"use_sim_time": use_sim_time},
        ],
    )

    ld = LaunchDescription()
    ld.add_action(
        DeclareLaunchArgument("launch_rviz", default_value="true", description="Launch RViz?")
    )
    ld.add_action(
        DeclareLaunchArgument(
            "ur_type",
            default_value="ur5e",
            choices=["ur3", "ur3e", "ur5", "ur5e", "ur7e", "ur10", "ur10e", "ur12e", "ur16e", "ur15", "ur20", "ur30"],
        )
    )
    ld.add_action(
        DeclareLaunchArgument("use_sim_time", default_value="true")
    )

    ld.add_action(wait_robot_description)
    ld.add_action(
        RegisterEventHandler(
            OnProcessExit(
                target_action=wait_robot_description,
                on_exit=[move_group_node, rviz_node],
            )
        )
    )

    return ld
