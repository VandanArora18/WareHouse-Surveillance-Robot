"""
display.launch.py
-----------------
Launches robot_state_publisher + joint_state_publisher_gui + RViz2
for quick URDF inspection without Gazebo.

Usage:
  ros2 launch warehouse_robot_description display.launch.py
  ros2 launch warehouse_robot_description display.launch.py rviz_config:=my.rviz

Compatible: ROS 2 Humble, WSL2 Ubuntu 22.04
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_share = get_package_share_directory('warehouse_robot_description')

    # ---------- launch arguments ----------
    urdf_file = os.path.join(pkg_share, 'urdf', 'warehouse_robot.urdf.xacro')
    default_rviz_config = os.path.join(pkg_share, 'rviz', 'display.rviz')

    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation (Gazebo) clock if true')

    rviz_config_arg = DeclareLaunchArgument(
        'rviz_config',
        default_value=default_rviz_config,
        description='Full path to the RViz config file')

    use_sim_time = LaunchConfiguration('use_sim_time')
    rviz_config  = LaunchConfiguration('rviz_config')

    # ---------- robot description via xacro ----------
    # Must be wrapped as ParameterValue(str) so launch doesn't try to parse
    # the URDF XML as YAML (causes "Unable to parse as yaml" error).
    robot_description = ParameterValue(Command(['xacro ', urdf_file]), value_type=str)

    # ---------- nodes ----------
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': use_sim_time,
        }]
    )

    # GUI slider for manual joint control (wheels)
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )

    rviz2_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': use_sim_time}]
    )

    return LaunchDescription([
        use_sim_time_arg,
        rviz_config_arg,
        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz2_node,
    ])
