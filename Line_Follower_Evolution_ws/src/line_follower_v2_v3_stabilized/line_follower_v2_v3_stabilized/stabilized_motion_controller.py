import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, Bool
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Imu
import math

class StabilizedMotionController(Node):
    """
    V2-V3 Motion Layer: Closed-Loop Dual PID with Angular Damping.
    
    Control Laws:
    1. Line Centering Yaw Rate:
       omega_cmd = -K_p * e - K_d * de/dt - K_gyro * omega_imu
    2. Adaptive Velocity Profiling:
       v_cmd = v_max * max(0.3, 1.0 - alpha * |e| - beta * |omega_imu|)
    """
    def __init__(self):
        super().__init__('stabilized_motion_controller')
        
        self.declare_parameter('kp', 35.0)
        self.declare_parameter('kd', 2.5)
        self.declare_parameter('k_gyro_damping', 0.15)
        self.declare_parameter('v_max', 0.65) # High-speed line following (0.65 m/s)
        
        self.kp = self.get_parameter('kp').value
        self.kd = self.get_parameter('kd').value
        self.k_gyro = self.get_parameter('k_gyro_damping').value
        self.v_max = self.get_parameter('v_max').value
        
        self.last_error = 0.0
        self.last_time = self.get_clock().now()
        self.current_yaw_rate = 0.0
        
        # Subscriptions
        self.sub_error = self.create_subscription(Float32, '/v2_v3/line_centroid_error', self.error_callback, 10)
        self.sub_imu = self.create_subscription(Imu, '/v2_v3/imu', self.imu_callback, 10)
        self.sub_intersection = self.create_subscription(Bool, '/v2_v3/intersection_detected', self.intersection_callback, 10)
        
        self.pub_cmd = self.create_publisher(Twist, '/cmd_vel', 10)
        self.get_logger().info('Stabilized High-Performance Motion Controller running.')

    def imu_callback(self, msg: Imu):
        self.current_yaw_rate = msg.angular_velocity.z

    def intersection_callback(self, msg: Bool):
        if msg.data:
            self.get_logger().info('[V2-V3 Perception]: Intersection detected! Maintaining forward path.', throttle_duration_sec=1.0)

    def error_callback(self, msg: Float32):
        now = self.get_clock().now()
        dt = (now - self.last_time).nanoseconds * 1e-9
        if dt <= 0.0:
            dt = 0.02
            
        error = msg.data
        d_error = (error - self.last_error) / dt
        
        # 1. Closed-loop angular rate with IMU gyro damping
        omega = -self.kp * error - self.kd * d_error - self.k_gyro * self.current_yaw_rate
        
        # 2. Dynamic speed regulation: slow down on tight curves
        v = self.v_max * max(0.25, 1.0 - 15.0 * abs(error) - 0.2 * abs(self.current_yaw_rate))
        
        cmd = Twist()
        cmd.linear.x = v
        cmd.angular.z = omega
        self.pub_cmd.publish(cmd)
        
        self.last_error = error
        self.last_time = now

def main(args=None):
    rclpy.init(args=args)
    node = StabilizedMotionController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
