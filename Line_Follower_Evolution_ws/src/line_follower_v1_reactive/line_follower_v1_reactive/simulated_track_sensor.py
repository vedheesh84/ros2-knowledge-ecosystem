import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from std_msgs.msg import Float32MultiArray
import math
import random


class SimulatedTrackSensor(Node):
    """
    Simulates physical 2-channel IR reflectance over a synthetic S-curve line track (Article LFE-02).
    Adds realistic physical noise and ADC quantization.
    """
    def __init__(self):
        super().__init__('simulated_track_sensor')
        self.pub_ir = self.create_publisher(Float32MultiArray, '/v1/ir_raw', 10)
        self.timer = self.create_timer(0.02, self.publish_sensors) # 50 Hz
        self.t = 0.0

    def publish_sensors(self):
        self.t += 0.02
        # Synthetic track lateral offset e(t) = 0.03 * sin(0.8 * t)
        lateral_error = 0.03 * math.sin(0.8 * self.t)
        
        # Sensor 1 (Left at +0.025m) and Sensor 2 (Right at -0.025m)
        dist_left = abs(0.025 - lateral_error)
        dist_right = abs(-0.025 - lateral_error)
        
        # Gaussian reflectance profile: I = exp(-(dist / w)^2)
        w = 0.015
        left_val = math.exp(-(dist_left / w)**2) + random.gauss(0, 0.02)
        right_val = math.exp(-(dist_right / w)**2) + random.gauss(0, 0.02)
        
        msg = Float32MultiArray()
        msg.data = [float(max(0.0, min(1.0, left_val))), float(max(0.0, min(1.0, right_val)))]
        self.pub_ir.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = SimulatedTrackSensor()
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
