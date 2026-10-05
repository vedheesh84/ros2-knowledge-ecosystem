import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray, Float32, Bool
import numpy as np

class SensorArrayProcessor(Node):
    """
    V3 Perception Layer: Computes weighted line centroid e and flags intersection presence.
    
    Centroid Equation:
    e = \frac{\sum_{i=1}^{N} w_i \cdot I_i}{\sum_{i=1}^{N} I_i}
    where w_i are spatial coordinates of the sensors [-3.5d, ..., +3.5d].
    
    Intersection Detection:
    If active_count >= 6 out of 8 sensors, flags intersection_detected = True.
    """
    def __init__(self):
        super().__init__('sensor_array_processor')
        
        # 8 IR sensor positions across 70mm bar (-35mm to +35mm)
        self.sensor_weights = np.linspace(-0.035, 0.035, 8)
        
        self.sub_raw_array = self.create_subscription(
            Float32MultiArray, '/v2_v3/ir_raw_array', self.raw_array_callback, 10
        )
        self.pub_centroid_error = self.create_publisher(Float32, '/v2_v3/line_centroid_error', 10)
        self.pub_intersection_flag = self.create_publisher(Bool, '/v2_v3/intersection_detected', 10)
        
        self.get_logger().info('8-Channel Sensor Array Perception Processor active.')

    def raw_array_callback(self, msg: Float32MultiArray):
        readings = np.array(msg.data)
        if len(readings) != 8:
            return
            
        total_intensity = np.sum(readings)
        active_sensors = np.sum(readings > 0.6)
        
        # 1. Intersection detection (all-black crossbar)
        intersection_msg = Bool()
        intersection_msg.data = bool(active_sensors >= 6)
        self.pub_intersection_flag.publish(intersection_msg)
        
        # 2. Weighted centroid error calculation
        error_msg = Float32()
        if total_intensity > 0.1:
            error_m = float(np.sum(self.sensor_weights * readings) / total_intensity)
            error_msg.data = error_m
        else:
            error_msg.data = 0.0 # Blind on loss
            
        self.pub_centroid_error.publish(error_msg)

def main(args=None):
    rclpy.init(args=args)
    node = SensorArrayProcessor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
