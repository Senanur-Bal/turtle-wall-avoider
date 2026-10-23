import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose


class DuvarKacisNode(Node):
    def __init__(self):
        super().__init__('duvar_kacis_node')

        self.declare_parameter('linear_speed', 1.5)
        self.declare_parameter('angular_speed', 2.0)
        self.declare_parameter('min_limit', 1.0)
        self.declare_parameter('max_limit', 10.0)

        self.linear_speed = self.get_parameter('linear_speed').value
        self.angular_speed = self.get_parameter('angular_speed').value
        self.min_limit = self.get_parameter('min_limit').value
        self.max_limit = self.get_parameter('max_limit').value

        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.subscription = self.create_subscription(
            Pose, '/turtle1/pose', self.pose_callback, 10)

        self.current_pose = None
        self.timer = self.create_timer(1.0, self.log_pose_callback)
        self.get_logger().info('Duvardan Kaçan Kaplumbağa Düğümü Başlatıldı!')

    def pose_callback(self, msg):
        self.current_pose = msg
        twist = Twist()

        # Duvara doğru mu gidiyor? (yön vektörü ile kontrol)
        dx = math.cos(msg.theta)
        dy = math.sin(msg.theta)

        hitting = (
            (msg.x > self.max_limit and dx > 0) or
            (msg.x < self.min_limit and dx < 0) or
            (msg.y > self.max_limit and dy > 0) or
            (msg.y < self.min_limit and dy < 0)
        )

        if hitting:
            twist.linear.x = 0.0                  # dur ve dön
            twist.angular.z = self.angular_speed
        else:
            twist.linear.x = self.linear_speed    # ileri git
            twist.angular.z = 0.0

        self.publisher_.publish(twist)

    def log_pose_callback(self):
        if self.current_pose is not None:
            self.get_logger().info(
                f'Mevcut Konum -> x: {self.current_pose.x:.2f}, y: {self.current_pose.y:.2f}')


def main(args=None):
    rclpy.init(args=args)
    node = DuvarKacisNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
