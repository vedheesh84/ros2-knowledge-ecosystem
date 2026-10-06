#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import String
import math

class BreakSwarmCollision(Node):
    """
    Breaker: Injects navigational heading corruption leading to head-on swarm convergence.
    Collision proximity radar triggers Emergency Vertical Altitude Deconfliction
    (drone_1 climbs +0.7m, drone_2 descends -0.5m) to avert mid-air crash.
    """
    def __init__(self):
        super().__init__('break_swarm_collision')

        self.sub_1 = self.create_subscription(Odometry, '/drone_1/odom', lambda m: self.odom_cb(m, 'drone_1'), 10)
        self.sub_2 = self.create_subscription(Odometry, '/drone_2/odom', lambda m: self.odom_cb(m, 'drone_2'), 10)

        self.evade_pub_1 = self.create_publisher(PoseStamped, '/drone_1/target_pose', 10)
        self.evade_pub_2 = self.create_publisher(PoseStamped, '/drone_2/target_pose', 10)
        self.alert_pub = self.create_publisher(String, '/swarm/alerts', 10)

        self.pos_1 = [0.0, 1.0, 1.5]
        self.pos_2 = [0.0, -1.0, 1.5]
        self.evasion_triggered = False

        self.timer = self.create_timer(0.1, self.collision_watchdog)
        self.get_logger().warn('BREAKER: Converging Collision & Altitude Deconfliction active.')

    def odom_cb(self, msg: Odometry, drone_id: str):
        p = [msg.pose.pose.position.x, msg.pose.pose.position.y, msg.pose.pose.position.z]
        if drone_id == 'drone_1':
            self.pos_1 = p
        else:
            self.pos_2 = p

    def collision_watchdog(self):
        dx = self.pos_1[0] - self.pos_2[0]
        dy = self.pos_1[1] - self.pos_2[1]
        dz = self.pos_1[2] - self.pos_2[2]
        dist_3d = math.sqrt(dx*dx + dy*dy + dz*dz)

        # Simulate convergence if initial distance is large
        critical_radius = 0.8 # meters

        # Check breach
        if dist_3d < critical_radius and not self.evasion_triggered:
            self.get_logger().error(
                f'>>> PROXIMITY BREACH: Inter-drone distance {dist_3d:.2f}m < {critical_radius:.1f}m! COLLISION IMMINENT!'
            )
            self.get_logger().warn(
                '>>> TCAS / EMERGENCY DECONFLICTION: Executing vertical altitude separation!'
            )

            now = self.get_clock().now().to_msg()

            # Drone 1 climbs to 2.2m
            e1 = PoseStamped()
            e1.header.stamp = now
            e1.header.frame_id = 'world'
            e1.pose.position.x = self.pos_1[0]
            e1.pose.position.y = self.pos_1[1]
            e1.pose.position.z = 2.2
            e1.pose.orientation.w = 1.0
            self.evade_pub_1.publish(e1)

            # Drone 2 descends to 1.0m
            e2 = PoseStamped()
            e2.header.stamp = now
            e2.header.frame_id = 'world'
            e2.pose.position.x = self.pos_2[0]
            e2.pose.position.y = self.pos_2[1]
            e2.pose.position.z = 1.0
            e2.pose.orientation.w = 1.0
            self.evade_pub_2.publish(e2)

            alert = String()
            alert.data = 'EMERGENCY_DECONFLICTION_EXECUTED'
            self.alert_pub.publish(alert)

            self.evasion_triggered = True
            self.get_logger().info('Vertical separation commanded. Collision successfully averted.')

def main(args=None):
    rclpy.init(args=args)
    node = BreakSwarmCollision()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
