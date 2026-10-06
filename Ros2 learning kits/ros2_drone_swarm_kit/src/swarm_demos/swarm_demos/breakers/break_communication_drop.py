#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseStamped
import time

class BreakCommDrop(Node):
    """
    Breaker: Injects packet drop / RF link failure between Leader (drone_0)
    and Follower (drone_2). Follower heartbeat watchdog triggers autonomous hover hold.
    """
    def __init__(self):
        super().__init__('break_comm_drop')
        
        self.sub = self.create_subscription(Odometry, '/drone_0/odom', self.leader_cb, 10)
        self.hover_pub = self.create_publisher(PoseStamped, '/drone_2/target_pose', 10)
        
        self.last_heartbeat = time.time()
        self.packets_received = 0
        self.fault_injected = False
        self.hover_hold_engaged = False
        
        # Check heartbeat watchdog at 10 Hz
        self.timer = self.create_timer(0.1, self.watchdog_check)
        self.get_logger().warn('BREAKER: Communication Drop Watchdog active for follower drone_2.')

    def leader_cb(self, msg: Odometry):
        self.packets_received += 1
        # Inject fault after 20 packets: drop all subsequent packets
        if self.packets_received > 20:
            if not self.fault_injected:
                self.get_logger().error('>>> INJECTING FAULT: Total RF communication drop with drone_0!')
                self.fault_injected = True
            return # Drop packet without updating timestamp

        self.last_heartbeat = time.time()

    def watchdog_check(self):
        elapsed = time.time() - self.last_heartbeat
        timeout_threshold = 1.0 # 1 second timeout

        if self.fault_injected and elapsed > timeout_threshold:
            if not self.hover_hold_engaged:
                self.get_logger().error(
                    f'[drone_2] CRITICAL: Heartbeat timeout ({elapsed:.2f}s > {timeout_threshold:.1f}s)! '
                    f'Disengaging formation and locking autonomous hover hold.'
                )
                self.hover_hold_engaged = True
                
                # Command hover hold at safe altitude
                hover_pose = PoseStamped()
                hover_pose.header.stamp = self.get_clock().now().to_msg()
                hover_pose.header.frame_id = 'world'
                hover_pose.pose.position.x = -1.0
                hover_pose.pose.position.y = -1.0
                hover_pose.pose.position.z = 1.5
                hover_pose.pose.orientation.w = 1.0
                self.hover_pub.publish(hover_pose)

def main(args=None):
    rclpy.init(args=args)
    node = BreakCommDrop()
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
