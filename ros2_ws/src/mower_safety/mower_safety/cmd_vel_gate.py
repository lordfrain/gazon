import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import Bool


class CmdVelGate(Node):
    """Sits between teleop and the diff_drive plugin: passes /cmd_vel through
    to /cmd_vel_out unless safety_watchdog has raised /safety/estop, in which
    case it forces zero velocity regardless of what teleop is asking for."""

    def __init__(self):
        super().__init__('cmd_vel_gate')
        self.estop = False
        self.pub = self.create_publisher(Twist, 'cmd_vel_out', 10)
        self.create_subscription(Bool, 'safety/estop', self.estop_callback, 10)
        self.create_subscription(Twist, 'cmd_vel', self.cmd_vel_callback, 10)

    def estop_callback(self, msg: Bool):
        was_estop = self.estop
        self.estop = msg.data
        if self.estop and not was_estop:
            self.pub.publish(Twist())  # stop immediately, don't wait for the next cmd_vel

    def cmd_vel_callback(self, msg: Twist):
        self.pub.publish(Twist() if self.estop else msg)


def main(args=None):
    rclpy.init(args=args)
    node = CmdVelGate()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
