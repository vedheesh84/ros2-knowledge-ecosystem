#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import String

class SwarmDispatchNode(Node):
    """
    High-level swarm mission dispatch coordinator.
    Manages collective mission states: IDLE, TAKEOFF, FORMATION, HOVER, RTH, LAND.
    """
    def __init__(self):
        super().__init__('swarm_dispatch_node')
        
        self.cmd_sub = self.create_subscription(String, '/swarm/mission_cmd', self.cmd_cb, 10)
        self.status_pub = self.create_publisher(String, '/swarm/mission_status', 10)
        self.formation_pub = self.create_publisher(String, '/swarm/formation_mode', 10)
        
        self.drone_pubs = {
            'drone_0': self.create_publisher(PoseStamped, '/drone_0/target_pose', 10),
            'drone_1': self.create_publisher(PoseStamped, '/drone_1/target_pose', 10),
            'drone_2': self.create_publisher(PoseStamped, '/drone_2/target_pose', 10),
        }

        self.state = 'IDLE'
        self.timer = self.create_timer(0.2, self.publish_status) # 5 Hz status
        self.get_logger().info('Swarm Dispatch Node initialized in state: IDLE.')
        self.publish_status()

    def cmd_cb(self, msg: String):
        cmd = msg.data.strip().upper()
        self.get_logger().info(f'Received Mission Command: {cmd}')
        now = self.get_clock().now().to_msg()

        if cmd == 'TAKEOFF':
            self.state = 'TAKEOFF'
            for d_id, pub in self.drone_pubs.items():
                p = PoseStamped()
                p.header.stamp = now
                p.header.frame_id = 'world'
                p.pose.position.z = 1.5
                p.pose.orientation.w = 1.0
                pub.publish(p)
        elif cmd in ['FORM_V', 'V_SHAPE']:
            self.state = 'FORMATION_V'
            mode_msg = String()
            mode_msg.data = 'V_SHAPE'
            self.formation_pub.publish(mode_msg)
        elif cmd in ['FORM_LINE', 'LINE']:
            self.state = 'FORMATION_LINE'
            mode_msg = String()
            mode_msg.data = 'LINE'
            self.formation_pub.publish(mode_msg)
        elif cmd in ['FORM_CIRCLE', 'CIRCLE']:
            self.state = 'FORMATION_CIRCLE'
            mode_msg = String()
            mode_msg.data = 'CIRCLE'
            self.formation_pub.publish(mode_msg)
        elif cmd == 'RTH':
            self.state = 'RTH'
            coords = {'drone_0': (0.0, 0.0), 'drone_1': (-1.0, 1.0), 'drone_2': (-1.0, -1.0)}
            for d_id, (x, y) in coords.items():
                p = PoseStamped()
                p.header.stamp = now
                p.header.frame_id = 'world'
                p.pose.position.x = x
                p.pose.position.y = y
                p.pose.position.z = 1.5
                p.pose.orientation.w = 1.0
                self.drone_pubs[d_id].publish(p)
        elif cmd == 'LAND':
            self.state = 'LANDING'
            for d_id, pub in self.drone_pubs.items():
                p = PoseStamped()
                p.header.stamp = now
                p.header.frame_id = 'world'
                p.pose.position.z = 0.0
                p.pose.orientation.w = 1.0
                pub.publish(p)
        else:
            self.get_logger().warn(f'Unrecognized mission command: {cmd}')

    def publish_status(self):
        msg = String()
        msg.data = f'MISSION_STATE: {self.state}'
        self.status_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = SwarmDispatchNode()
    try:
        rclpy.spin(node)
    except Exception:
        pass
    finally:
        try:
            node.destroy_node()
        except Exception:
            pass
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
