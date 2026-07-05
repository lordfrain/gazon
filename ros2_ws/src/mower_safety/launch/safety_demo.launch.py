from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='mower_safety',
            executable='fake_lidar_publisher',
            name='fake_lidar_publisher',
            output='screen',
        ),
        Node(
            package='mower_safety',
            executable='safety_watchdog',
            name='safety_watchdog',
            output='screen',
            parameters=[{
                'danger_distance_m': 1.0,
                'danger_arc_deg': 60.0,
            }],
        ),
    ])
