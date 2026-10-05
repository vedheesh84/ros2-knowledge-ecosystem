import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from geometry_msgs.msg import PoseStamped
from arm_kinematics.forward_kinematics import ForwardKinematics
from arm_kinematics.inverse_kinematics import InverseKinematics

class KinematicsServiceNode(Node):
    def __init__(self):
        super().__init__('arm_kinematics_node')
        self.fk = ForwardKinematics()
        self.ik = InverseKinematics()
        
        self.joint_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            10
        )
        self.pose_pub = self.create_publisher(PoseStamped, '/arm/end_effector_pose', 10)
        self.get_logger().info('Arm Kinematics Node online. Publishing calculated end-effector pose.')

    def joint_state_callback(self, msg: JointState):
        name_map = dict(zip(msg.name, msg.position))
        q1 = name_map.get('joint_1', 0.0)
        q2 = name_map.get('joint_2', 0.0)
        q3 = name_map.get('joint_3', 0.0)
        q4 = name_map.get('joint_4', 0.0)
        
        x, y, z, pitch = self.fk.compute_fk(q1, q2, q3, q4)
        
        pose_msg = PoseStamped()
        pose_msg.header.stamp = self.get_clock().now().to_msg()
        pose_msg.header.frame_id = 'base_link'
        pose_msg.pose.position.x = float(x)
        pose_msg.pose.position.y = float(y)
        pose_msg.pose.position.z = float(z)
        self.pose_pub.publish(pose_msg)

def main(args=None):
    rclpy.init(args=args)
    node = KinematicsServiceNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
