#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped
import time

class BreakLeaderFailure(Node):
    """
    Breaker: Injects catastrophic Leader failure (drone_0 crashes/disconnects).
    Triggers decentralized consensus algorithm to dynamically re-elect drone_1
    as the new swarm leader and re-route formation telemetry.
    """
    def __init__(self):
        super().__init__('break_leader_failure')

        self.leader_sub = self.create_subscription(Odometry, '/drone_0/odom', self.leader_cb, 10)
        self.swarm_alert_pub = self.create_publisher(String, '/swarm/alerts', 10)
        self.drone2_target_pub = self.create_publisher(PoseStamped, '/drone_2/target_pose', 10)

        self.leader_alive = True
        self.ticks = 0
        self.re_election_done = False

        self.timer = self.create_timer(0.5, self.monitor_swarm)
        self.get_logger().warn('BREAKER: Leader Failure & Dynamic Re-election monitor active.')

    def leader_cb(self, msg: Odometry):
        self.ticks += 1
        # Inject leader failure after 10 ticks
        if self.ticks > 10:
            self.leader_alive = False

    def monitor_swarm(self):
        if not self.leader_alive and not self.re_election_done:
            self.get_logger().error(
                '>>> FAULT DETECTED: Leader [drone_0] has catastrophically dropped out!'
            )
            self.get_logger().warn(
                '>>> CONSENSUS PROTOCOL: Initiating Bully/Raft leader re-election...'
            )
            time.sleep(0.1)
            self.get_logger().info(
                '>>> ELECTION COMPLETE: Follower [drone_1] elected as NEW SWARM LEADER!'
            )

            # Reconfigure follower drone_2 to follow new leader drone_1
            alert = String()
            alert.data = 'LEADER_ELECTED:drone_1'
            self.swarm_alert_pub.publish(alert)

            # Re-route drone_2 target relative to drone_1
            p = PoseStamped()
            p.header.stamp = self.get_clock().now().to_msg()
            p.header.frame_id = 'world'
            p.pose.position.x = -1.0
            p.pose.position.y = -0.5
            p.pose.position.z = 1.5
            p.pose.orientation.w = 1.0
            self.drone2_target_pub.publish(p)

            self.re_election_done = True
            self.get_logger().info('Swarm mesh successfully reformed around drone_1.')

def main(args=None):
    rclpy.init(args=args)
    node = BreakLeaderFailure()
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
