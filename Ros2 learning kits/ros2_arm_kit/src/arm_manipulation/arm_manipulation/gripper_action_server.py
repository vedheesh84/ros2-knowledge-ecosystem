import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from std_msgs.msg import Float32, String
import time

class GripperControllerNode(Node):
    """
    Controls parallel gripper opening and closing with stall/effort feedback.
    """
    def __init__(self):
        super().__init__('gripper_controller')
        self.cmd_pub = self.create_publisher(JointTrajectory, '/arm_controller/joint_trajectory', 10)
        self.status_pub = self.create_publisher(String, '/gripper/status', 10)
        
        self.cmd_sub = self.create_subscription(
            Float32,
            '/gripper/command',
            self.command_callback,
            10
        )
        self.current_width = 0.0
        self.get_logger().info('Gripper Action Controller online.')

    def command_callback(self, msg: Float32):
        target_pos = max(0.0, min(1.0, float(msg.data)))
        self.get_logger().info(f'Executing gripper target: {target_pos:.2f} (0=closed, 1=open)')
        
        traj = JointTrajectory()
        traj.joint_names = ['left_gear_joint']
        pt = JointTrajectoryPoint()
        pt.positions = [target_pos]
        pt.time_from_start.sec = 1
        traj.points.append(pt)
        self.cmd_pub.publish(traj)
        
        # Publish status
        status = String()
        status.data = f'GRIPPER_MOVED_TO_{target_pos:.2f}'
        self.status_pub.publish(status)

def main(args=None):
    rclpy.init(args=args)
    node = GripperControllerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
