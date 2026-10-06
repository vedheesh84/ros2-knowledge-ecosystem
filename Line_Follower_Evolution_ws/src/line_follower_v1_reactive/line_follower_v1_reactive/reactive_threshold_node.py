import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from std_msgs.msg import Float32MultiArray, String
from geometry_msgs.msg import Twist


class ReactiveThresholdNode(Node):
    """
    Line Follower V1: Pure Reactive Bang-Bang / Threshold Controller (Article LFE-02).
    
    Demonstrates fundamental physical challenges:
    1. Zero velocity regulation: Motor commands are raw PWM-like twist values.
    2. Bang-bang oscillation: Left/Right toggling causes severe zigzag overshoot.
    3. Latency fragility: Reaction time delay tau causes trajectory departure at higher speeds.
    """
    def __init__(self):
        super().__init__('reactive_threshold_node')
        
        self.declare_parameter('forward_speed', 0.22)   # m/s nominal
        self.declare_parameter('turn_angular_rate', 1.8) # rad/s aggressive bang-bang turn
        self.declare_parameter('threshold_analog', 0.5)  # 0.0 = white floor, 1.0 = black line
        
        self.v_fwd = float(self.get_parameter('forward_speed').value)
        self.omega_turn = float(self.get_parameter('turn_angular_rate').value)
        self.threshold = float(self.get_parameter('threshold_analog').value)
        
        # Subscriptions
        self.sub_ir = self.create_subscription(
            Float32MultiArray, '/v1/ir_raw', self.ir_callback, 10
        )
        
        # Publishers
        self.pub_cmd = self.create_publisher(Twist, '/cmd_vel', 10)
        self.pub_diag = self.create_publisher(String, '/v1/diagnostics', 10)
        
        self.last_state = "ON_LINE"
        self.get_logger().info('Line Follower V1 (Reactive Threshold Tracker) initialized.')

    def ir_callback(self, msg: Float32MultiArray):
        if len(msg.data) < 2:
            return
            
        left_ir = msg.data[0]   # Value in [0.0, 1.0]
        right_ir = msg.data[1]  # Value in [0.0, 1.0]
        
        cmd = Twist()
        
        # Binary Thresholding Logic:
        left_on_line = left_ir > self.threshold
        right_on_line = right_ir > self.threshold
        
        if left_on_line and right_on_line:
            # Centered on line: drive straight
            cmd.linear.x = self.v_fwd
            cmd.angular.z = 0.0
            self.last_state = "CENTERED"
        elif left_on_line and not right_on_line:
            # Line shifted to the left: hard bang-bang left turn
            cmd.linear.x = self.v_fwd * 0.5  # Fixed speed drop
            cmd.angular.z = self.omega_turn
            self.last_state = "TURN_LEFT_OVERSHOOT"
        elif right_on_line and not left_on_line:
            # Line shifted to the right: hard bang-bang right turn
            cmd.linear.x = self.v_fwd * 0.5
            cmd.angular.z = -self.omega_turn
            self.last_state = "TURN_RIGHT_OVERSHOOT"
        else:
            # Off line completely (lost tracking due to momentum overshoot)
            cmd.linear.x = 0.0
            cmd.angular.z = self.omega_turn * 1.2 # Blind recovery spin
            self.last_state = "LOST_LINE_SEARCHING"
            
        self.pub_cmd.publish(cmd)
        
        diag = String()
        diag.data = f"State: {self.last_state} | L_IR: {left_ir:.2f} | R_IR: {right_ir:.2f}"
        self.pub_diag.publish(diag)


def main(args=None):
    rclpy.init(args=args)
    node = ReactiveThresholdNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
