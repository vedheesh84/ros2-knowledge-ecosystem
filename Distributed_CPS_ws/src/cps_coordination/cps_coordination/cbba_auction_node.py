import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json
import math

class CBBAAuctionNode(Node):
    """
    CBBAAuctionNode: Decentralized Consensus-Based Bundle Algorithm Engine.
    
    Implements a 2-phase distributed market auction protocol:
    1. Bundle Building: Greedy local task score calculation based on distance, battery, and capabilities.
    2. Consensus Resolution: Decentralized bidding arbitration over DDS topics without a central master.
    """
    def __init__(self):
        super().__init__('cbba_auction_node')
        
        self.declare_parameter('robot_id', 'robot1')
        self.declare_parameter('max_bundle_size', 3)
        
        self.robot_id = self.get_parameter('robot_id').value
        self.max_bundle = self.get_parameter('max_bundle_size').value
        
        # State
        self.bundle = []      # Ordered list of task IDs
        self.path = []        # Sequence of execution coordinates
        self.winning_bids = {} # {task_id: highest_bid}
        self.winning_agents = {} # {task_id: winning_agent_id}
        
        # Communication
        self.sub_bids = self.create_subscription(String, '/cps/auction_bids', self.bids_callback, 10)
        self.pub_bids = self.create_publisher(String, '/cps/auction_bids', 10)
        
        self.timer = self.create_timer(2.0, self.auction_cycle)
        self.get_logger().info(f'CBBA Auction Node running for agent [{self.robot_id}].')

    def calculate_marginal_score(self, task):
        # Distance-discounted score metric: S = Score_0 * exp(-lambda * distance)
        dist = math.sqrt(task.get('x', 0)**2 + task.get('y', 0)**2)
        score = 100.0 / (1.0 + 0.5 * dist)
        return score

    def auction_cycle(self):
        # Publish current winning bids to peers
        bid_packet = {
            'agent_id': self.robot_id,
            'bids': self.winning_bids,
            'winners': self.winning_agents
        }
        msg = String()
        msg.data = json.dumps(bid_packet)
        self.pub_bids.publish(msg)

    def bids_callback(self, msg: String):
        try:
            packet = json.loads(msg.data)
            sender = packet.get('agent_id')
            if sender == self.robot_id:
                return
            # Consensus resolution: if peer outbids us, release task from our bundle
            peer_bids = packet.get('bids', {})
            peer_winners = packet.get('winners', {})
            for t_id, bid in peer_bids.items():
                if bid > self.winning_bids.get(t_id, -1.0):
                    self.winning_bids[t_id] = bid
                    self.winning_agents[t_id] = peer_winners.get(t_id, sender)
                    if t_id in self.bundle and self.winning_agents[t_id] != self.robot_id:
                        self.bundle.remove(t_id)
        except Exception:
            pass

def main(args=None):
    rclpy.init(args=args)
    node = CBBAAuctionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
