import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import time

class TagDetectorNode(Node):
    """
    Simulates visual node tag identification (AprilTag / ArUco / QR) as the robot traverses the track.
    """
    def __init__(self):
        super().__init__('tag_detector_node')
        self.pub_tag = self.create_publisher(String, '/v4_v5/detected_node_tag', 10)
        self.get_logger().info('Tag Detector Node initialized.')

    def simulate_tag_detection(self, tag_id: str):
        msg = String()
        msg.data = tag_id
        self.pub_tag.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = TagDetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
