#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from arm_kinematics.inverse_kinematics import InverseKinematics

class BreakIkSingularity(Node):
    """Breaker: Tests unreachable Cartesian coordinates outside the workspace radius."""
    def __init__(self):
        super().__init__('break_ik_singularity')
        self.ik = InverseKinematics()
        self.timer = self.create_timer(2.0, self.test_unreachable)
        self.get_logger().warn('BREAKER: Requesting unreachable target (X=1.5m, Y=1.5m).')

    def test_unreachable(self):
        sol = self.ik.solve(1.5, 1.5, 0.5)
        if sol is None:
            self.get_logger().error('IK Solver correctly rejected out-of-reach target (1.5, 1.5, 0.5)!')
        else:
            self.get_logger().info('Solved (unexpected)')

def main(args=None):
    rclpy.init(args=args)
    node = BreakIkSingularity()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
