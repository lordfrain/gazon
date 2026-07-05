import math

import rclpy
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool


class SafetyWatchdog(Node):
    """Subscribes to /scan and publishes True on /safety/estop whenever
    something is closer than danger_distance_m within the front arc.
    This is the node that will eventually gate power to the blade motor."""

    def __init__(self):
        super().__init__('safety_watchdog')
        self.declare_parameter('danger_distance_m', 1.0)
        self.declare_parameter('danger_arc_deg', 60.0)

        qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT,
                          history=HistoryPolicy.KEEP_LAST)
        self.subscription = self.create_subscription(LaserScan, 'scan', self.scan_callback, qos)
        self.estop_pub = self.create_publisher(Bool, 'safety/estop', 10)
        self.last_state = None

    def scan_callback(self, msg: LaserScan):
        danger_distance = self.get_parameter('danger_distance_m').value
        danger_arc_deg = self.get_parameter('danger_arc_deg').value
        half_arc_rad = math.radians(danger_arc_deg / 2.0)

        min_range_in_arc = msg.range_max
        for i, r in enumerate(msg.ranges):
            angle = msg.angle_min + i * msg.angle_increment
            norm_angle = math.atan2(math.sin(angle), math.cos(angle))
            if abs(norm_angle) <= half_arc_rad and msg.range_min < r < msg.range_max:
                min_range_in_arc = min(min_range_in_arc, r)

        should_stop = min_range_in_arc < danger_distance

        if should_stop != self.last_state:
            if should_stop:
                self.get_logger().warn(
                    f'STOP: object at {min_range_in_arc:.2f} m (threshold {danger_distance:.2f} m)')
            else:
                self.get_logger().info('Clear: resuming allowed')
            self.last_state = should_stop

        self.estop_pub.publish(Bool(data=should_stop))


def main(args=None):
    rclpy.init(args=args)
    node = SafetyWatchdog()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
