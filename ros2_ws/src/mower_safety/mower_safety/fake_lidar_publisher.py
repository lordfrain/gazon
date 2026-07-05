import math

import rclpy
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import LaserScan


class FakeLidarPublisher(Node):
    """Stand-in for the LD19 driver: publishes LaserScan on /scan with a
    simulated obstacle that approaches and retreats, so safety_watchdog can
    be developed and tested before the real lidar arrives."""

    def __init__(self):
        super().__init__('fake_lidar_publisher')
        qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT,
                          history=HistoryPolicy.KEEP_LAST)
        self.publisher_ = self.create_publisher(LaserScan, 'scan', qos)
        self.timer = self.create_timer(0.1, self.publish_scan)  # 10 Hz, like LD19
        self.num_readings = 360
        self.max_range = 12.0  # LD19 max range ~12 m
        self.t = 0.0

    def publish_scan(self):
        msg = LaserScan()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'laser'
        msg.angle_min = 0.0
        msg.angle_max = 2 * math.pi
        msg.angle_increment = 2 * math.pi / self.num_readings
        msg.time_increment = 0.0
        msg.scan_time = 0.1
        msg.range_min = 0.02
        msg.range_max = self.max_range

        ranges = [self.max_range] * self.num_readings

        cycle_s = 10.0
        phase = (self.t % cycle_s) / cycle_s
        if phase < 0.5:
            distance = self.max_range - (self.max_range - 0.3) * (phase / 0.5)
        else:
            distance = 0.3 + (self.max_range - 0.3) * ((phase - 0.5) / 0.5)

        obstacle_width_deg = 10
        for i in range(obstacle_width_deg):
            ranges[i % self.num_readings] = distance

        msg.ranges = ranges
        msg.intensities = []
        self.publisher_.publish(msg)
        self.t += 0.1


def main(args=None):
    rclpy.init(args=args)
    node = FakeLidarPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
