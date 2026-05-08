"""
gazebo.launch.py
Warehouse Robot — Ignition Fortress + SLAM Toolbox (online async)
ROS 2 Humble, WSL2 Ubuntu 22.04

Nodes launched:
  1. SetEnvironmentVariable  — IGN_GAZEBO_RESOURCE_PATH
  2. Ignition Gazebo          — warehouse_factory.sdf world
  3. robot_state_publisher    — URDF → /robot_description + static TF
  4. joint_state_publisher    — publishes caster/arm joint states
  5. ros_gz_bridge            — bridges all IGN↔ROS topics
  6. spawn_robot              — spawns robot after 10 s delay
  7. slam_toolbox             — online async SLAM → /map + map→odom TF

Usage:
  ros2 launch warehouse_robot_description gazebo.launch.py
  ros2 launch warehouse_robot_description gazebo.launch.py open_rviz:=true
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (IncludeLaunchDescription, TimerAction,
                             SetEnvironmentVariable, DeclareLaunchArgument)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.substitutions import Command
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():

    pkg_path   = get_package_share_directory('warehouse_robot_description')
    urdf_file  = os.path.join(pkg_path, 'urdf',   'warehouse_robot.urdf.xacro')
    world_file = os.path.join(pkg_path, 'worlds', 'warehouse_factory.sdf')
    bridge_cfg = os.path.join(pkg_path, 'config', 'ros_gz_bridge.yaml')
    slam_cfg   = os.path.join(pkg_path, 'config', 'slam_params.yaml')
    rviz_cfg   = os.path.join(pkg_path, 'rviz',   'slam.rviz')

    # ── Launch args ────────────────────────────────────────────────
    open_rviz_arg = DeclareLaunchArgument(
        'open_rviz', default_value='false',
        description='Open RViz2 with SLAM view')

    open_rviz = LaunchConfiguration('open_rviz')

    robot_description = ParameterValue(
        Command(['xacro ', urdf_file]),
        value_type=str
    )

    # ── 1. Environment variable (must be first) ────────────────────
    # Points to share/ parent so Ignition finds warehouse_robot_description/
    # as a model folder when resolving package:// URIs
    set_ign_resource_path = SetEnvironmentVariable(
        name='IGN_GAZEBO_RESOURCE_PATH',
        value=os.path.join(pkg_path, '..')
    )

    # ── 2. Ignition Gazebo with warehouse world ────────────────────
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('ros_gz_sim'),
                'launch', 'gz_sim.launch.py'
            )
        ),
        launch_arguments={
            'gz_args': '-r ' + world_file,
            'on_exit_shutdown': 'true'
        }.items()
    )

    # ── 3. Robot State Publisher ───────────────────────────────────
    # Publishes /robot_description and all static TF frames:
    # base_footprint→base_link→lidar_link, base_link→arm_base→...
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True
        }],
        output='screen'
    )

    # ── 4. Joint State Publisher ───────────────────────────────────
    # Publishes states for joints not driven by the diff drive plugin
    # (caster steer joints, arm joints).
    # source_list means it will MERGE with /joint_states from Gazebo plugin
    # rather than overwriting them.
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        parameters=[{
            'use_sim_time': True,
            'source_list': ['/joint_states'],
            'rate': 30
        }],
        output='screen'
    )

    # ── 5. ROS-Gazebo Bridge ───────────────────────────────────────
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'config_file': bridge_cfg}],
        output='screen'
    )

    # ── 6. Spawn robot (10 s delay lets Gazebo fully initialise) ──
    spawn_robot = TimerAction(
        period=10.0,
        actions=[
            Node(
                package='ros_gz_sim',
                executable='create',
                arguments=[
                    '-topic', '/robot_description',
                    '-name',  'warehouse_robot',
                    '-x', '0.0',
                    '-y', '0.0',
                    '-z', '0.2',
                ],
                output='screen'
            )
        ]
    )

    # ── 7. SLAM Toolbox (online async, starts after robot spawns) ──
    # Subscribes to: /scan, /tf, /tf_static
    # Publishes:     /map (OccupancyGrid), map→odom TF
    # The full TF chain for SLAM:
    #   map ← [slam_toolbox] ← odom ← [diff_drive] ← base_footprint
    #   ← [robot_state_publisher] ← base_link ← lidar_link
    slam = TimerAction(
        period=12.0,   # start 2 s after robot spawns
        actions=[
            Node(
                package='slam_toolbox',
                executable='async_slam_toolbox_node',
                name='slam_toolbox',
                parameters=[
                    slam_cfg,
                    {'use_sim_time': True}
                ],
                output='screen'
            )
        ]
    )

    # ── 8. RViz2 (optional, SLAM view) ────────────────────────────
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_cfg],
        parameters=[{'use_sim_time': True}],
        condition=IfCondition(open_rviz),
        output='screen'
    )

    static_odom_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_odom_broadcaster',
        arguments=['0', '0', '0', '0', '0', '0', 'odom', 'base_footprint'],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    static_lidar_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_lidar_broadcaster',
        arguments=['0', '0', '0.30', '0', '0', '0', 'base_link', 'lidar_link'],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )
    
    odom_to_path = Node(
    package='warehouse_robot_description',
    executable='odom_to_path.py',
    name='odom_to_path',
    parameters=[{'use_sim_time': True}],
    output='screen'
    )

    return LaunchDescription([
        open_rviz_arg,
        set_ign_resource_path,   # MUST be first
        gz_sim,
        robot_state_publisher,
        joint_state_publisher,
        bridge,
        static_odom_tf,
        static_lidar_tf,
        odom_to_path,
        spawn_robot,
        slam,
        rviz,
    ])