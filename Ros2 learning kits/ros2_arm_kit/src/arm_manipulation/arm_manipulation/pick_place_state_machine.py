import rclpy
from rclpy.node import Node
from enum import Enum
from std_msgs.msg import String, Float32
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from arm_kinematics.inverse_kinematics import InverseKinematics
import time

class ArmState(Enum):
    IDLE = 'IDLE'
    APPROACH = 'APPROACH'
    GRASP_OPEN = 'GRASP_OPEN'
    REACH_DOWN = 'REACH_DOWN'
    GRASP_CLOSE = 'GRASP_CLOSE'
    LIFT = 'LIFT'
    TRANSPORT = 'TRANSPORT'
    PLACE_DOWN = 'PLACE_DOWN'
    RELEASE = 'RELEASE'
    RETRACT = 'RETRACT'
    ERROR = 'ERROR'

class PickPlaceStateMachine(Node):
    """
    Autonomous State Machine coordinating complete tabletop Pick-and-Place sequence.
    """
    def __init__(self):
        super().__init__('pick_place_state_machine')
        self.state = ArmState.IDLE
        self.ik = InverseKinematics()
        
        self.arm_pub = self.create_publisher(JointTrajectory, '/arm_controller/joint_trajectory', 10)
        self.gripper_pub = self.create_publisher(Float32, '/gripper/command', 10)
        self.state_pub = self.create_publisher(String, '/arm/state', 10)
        
        self.timer = self.create_timer(1.5, self.state_tick)
        self.get_logger().info('Arm Pick & Place State Machine active.')

    def send_arm_joint_goals(self, q1, q2, q3, q4, q_wrist=0.0):
        traj = JointTrajectory()
        traj.joint_names = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'gripper_base_joint']
        pt = JointTrajectoryPoint()
        pt.positions = [float(q1), float(q2), float(q3), float(q4), float(q_wrist)]
        pt.time_from_start.sec = 1
        traj.points.append(pt)
        self.arm_pub.publish(traj)

    def state_tick(self):
        self.get_logger().info(f'Current State: {self.state.value}')
        
        if self.state == ArmState.IDLE:
            self.state = ArmState.GRASP_OPEN
            
        elif self.state == ArmState.GRASP_OPEN:
            # Open gripper
            self.gripper_pub.publish(Float32(data=1.0))
            self.state = ArmState.APPROACH
            
        elif self.state == ArmState.APPROACH:
            # Move above pick object: (x=0.18, y=0.0, z=0.15)
            sol = self.ik.solve(0.18, 0.0, 0.15, target_pitch=-0.7)
            if sol:
                self.send_arm_joint_goals(*sol)
                self.state = ArmState.REACH_DOWN
            else:
                self.state = ArmState.ERROR
                
        elif self.state == ArmState.REACH_DOWN:
            # Move down to grasp position: (x=0.18, y=0.0, z=0.04)
            sol = self.ik.solve(0.18, 0.0, 0.04, target_pitch=-0.7)
            if sol:
                self.send_arm_joint_goals(*sol)
                self.state = ArmState.GRASP_CLOSE
            else:
                self.state = ArmState.ERROR
                
        elif self.state == ArmState.GRASP_CLOSE:
            # Close gripper firmly
            self.gripper_pub.publish(Float32(data=0.0))
            self.state = ArmState.LIFT
            
        elif self.state == ArmState.LIFT:
            # Lift object upward: (x=0.18, y=0.0, z=0.18)
            sol = self.ik.solve(0.18, 0.0, 0.18, target_pitch=-0.5)
            if sol:
                self.send_arm_joint_goals(*sol)
                self.state = ArmState.TRANSPORT
            else:
                self.state = ArmState.ERROR
                
        elif self.state == ArmState.TRANSPORT:
            # Rotate base to target bin: (x=0.0, y=0.18, z=0.18)
            sol = self.ik.solve(0.0, 0.18, 0.18, target_pitch=-0.5)
            if sol:
                self.send_arm_joint_goals(*sol)
                self.state = ArmState.PLACE_DOWN
            else:
                self.state = ArmState.ERROR
                
        elif self.state == ArmState.PLACE_DOWN:
            # Lower to bin surface: (x=0.0, y=0.18, z=0.04)
            sol = self.ik.solve(0.0, 0.18, 0.04, target_pitch=-0.7)
            if sol:
                self.send_arm_joint_goals(*sol)
                self.state = ArmState.RELEASE
            else:
                self.state = ArmState.ERROR
                
        elif self.state == ArmState.RELEASE:
            # Release gripper
            self.gripper_pub.publish(Float32(data=1.0))
            self.state = ArmState.RETRACT
            
        elif self.state == ArmState.RETRACT:
            # Retract home: (q1=0, q2=0, q3=0, q4=0)
            self.send_arm_joint_goals(0.0, 0.0, 0.0, 0.0)
            self.get_logger().info('Pick and place cycle completed successfully.')
            self.state = ArmState.IDLE

        status = String()
        status.data = f'STATE:{self.state.value}'
        self.state_pub.publish(status)

def main(args=None):
    rclpy.init(args=args)
    node = PickPlaceStateMachine()
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

