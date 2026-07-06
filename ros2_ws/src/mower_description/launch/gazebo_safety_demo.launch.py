import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_description = get_package_share_directory('mower_description')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')

    world_path = os.path.join(pkg_description, 'worlds', 'mower_world.world')
    xacro_path = os.path.join(pkg_description, 'urdf', 'mower.urdf.xacro')

    robot_description = ParameterValue(Command(['xacro ', xacro_path]), value_type=str)

    gui_arg = DeclareLaunchArgument('gui', default_value='true')

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={'world': world_path, 'gui': LaunchConfiguration('gui')}.items(),
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description}],
    )

    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'mower', '-z', '0.1'],
        output='screen',
    )

    safety_watchdog = Node(
        package='mower_safety',
        executable='safety_watchdog',
        output='screen',
        parameters=[{'danger_distance_m': 1.0, 'danger_arc_deg': 60.0}],
    )

    cmd_vel_gate = Node(
        package='mower_safety',
        executable='cmd_vel_gate',
        output='screen',
    )

    return LaunchDescription([
        gui_arg,
        gazebo,
        robot_state_publisher,
        spawn_entity,
        safety_watchdog,
        cmd_vel_gate,
    ])
