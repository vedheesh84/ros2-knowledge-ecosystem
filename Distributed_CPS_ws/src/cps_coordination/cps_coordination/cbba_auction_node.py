import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped, Point
import json
import math
import time

try:
    from cps_msgs.msg import TaskAssignment, PeerState
    HAVE_CPS_MSGS = True
except ImportError:
    HAVE_CPS_MSGS = False


class CBBAAuctionNode(Node):
    """
    CBBAAuctionNode: Decentralized Consensus-Based Bundle Algorithm Engine.
    
    Implements a 2-phase distributed market auction protocol (Article CPS-06):
    1. Bundle Building (Phase 1): Greedy local task score calculation based on distance-discounted
       marginal rewards c_ij = R_j * exp(-lambda * ||x_i - x_j||). Tasks are greedily appended to
       the local bundle up to max_bundle_size if the marginal score exceeds the current winning bid.
    2. Consensus Resolution (Phase 2): Decentralized bidding arbitration over DDS topics without a
       central master. Peers exchange winning bids y_i and winning agents z_i. Outbid agents release
       conflicting tasks and all downstream bundle elements.
    """
    def __init__(self):
        super().__init__('cbba_auction_node')
        
        self.declare_parameter('robot_id', 'robot1')
        self.declare_parameter('max_bundle_size', 3)
        self.declare_parameter('lambda_discount', 0.1)
        self.declare_parameter('base_reward', 100.0)
        self.declare_parameter('agent_x', 0.0)
        self.declare_parameter('agent_y', 0.0)
        
        self.robot_id = str(self.get_parameter('robot_id').value)
        self.max_bundle = int(self.get_parameter('max_bundle_size').value)
        self.lambda_discount = float(self.get_parameter('lambda_discount').value)
        self.base_reward = float(self.get_parameter('base_reward').value)
        
        # Agent current pose
        self.agent_x = float(self.get_parameter('agent_x').value)
        self.agent_y = float(self.get_parameter('agent_y').value)
        
        # CBBA State vectors
        # Known tasks: {task_id: {'x': float, 'y': float, 'reward': float}}
        self.known_tasks = {}
        self.bundle = []             # Ordered list of task IDs: b_i
        self.path = []               # Sequence of coordinates for the bundle: p_i
        self.winning_bids = {}       # Winning bid list: y_i {task_id: float}
        self.winning_agents = {}     # Winning agent list: z_i {task_id: str}
        
        # Communication - Auction bids broadcast
        self.sub_bids = self.create_subscription(String, '/cps/auction_bids', self.bids_callback, 10)
        self.pub_bids = self.create_publisher(String, '/cps/auction_bids', 10)
        
        # Available tasks subscription (String JSON or TaskAssignment)
        self.sub_tasks_json = self.create_subscription(String, '/cps/available_tasks_json', self.tasks_json_callback, 10)
        if HAVE_CPS_MSGS:
            self.sub_tasks_typed = self.create_subscription(TaskAssignment, '/cps/available_tasks', self.tasks_typed_callback, 10)
            self.pub_peer_state = self.create_publisher(PeerState, f'/{self.robot_id}/peer_state', 10)
        else:
            self.sub_tasks_typed = None
            self.pub_peer_state = None
            
        # Pose subscription to update agent position
        self.sub_pose = self.create_subscription(PoseStamped, f'/{self.robot_id}/pose', self.pose_callback, 10)
        
        # Bundle state publisher
        self.pub_bundle = self.create_publisher(String, f'/{self.robot_id}/bundle', 10)
        
        # Periodic CBBA cycle (2.0 Hz)
        self.timer = self.create_timer(0.5, self.auction_cycle)
        self.get_logger().info(f'CBBA Auction Node running for agent [{self.robot_id}] with max_bundle={self.max_bundle}.')

    def pose_callback(self, msg: PoseStamped):
        """Updates agent's known 2D position for Euclidean travel distance calculations."""
        self.agent_x = msg.pose.position.x
        self.agent_y = msg.pose.position.y

    def add_task(self, task_id: str, x: float, y: float, reward: float = None):
        """Registers a newly discovered task into the agent's known task pool."""
        r = reward if reward is not None else self.base_reward
        self.known_tasks[task_id] = {'x': float(x), 'y': float(y), 'reward': float(r)}
        if task_id not in self.winning_bids:
            self.winning_bids[task_id] = 0.0
            self.winning_agents[task_id] = ''
        self.run_bundle_building()

    def tasks_json_callback(self, msg: String):
        try:
            data = json.loads(msg.data)
            t_id = data.get('task_id', f'task_{len(self.known_tasks)}')
            x = data.get('x', 0.0)
            y = data.get('y', 0.0)
            reward = data.get('reward', self.base_reward)
            self.add_task(t_id, x, y, reward)
        except Exception as e:
            self.get_logger().warn(f'Failed to parse task JSON: {e}')

    def tasks_typed_callback(self, msg: TaskAssignment):
        t_id = msg.task_id if msg.task_id else f'task_{len(self.known_tasks)}'
        x = msg.target_pose.pose.position.x
        y = msg.target_pose.pose.position.y
        reward = float(msg.priority * 2.0) if msg.priority > 0 else self.base_reward
        self.add_task(t_id, x, y, reward)

    def calculate_marginal_score(self, task_info: dict, current_x: float, current_y: float) -> float:
        """
        Calculates distance-discounted marginal score:
        c_ij = R_j * exp(-lambda * ||x_i - x_j||)
        """
        dx = task_info['x'] - current_x
        dy = task_info['y'] - current_y
        dist = math.hypot(dx, dy)
        score = task_info['reward'] * math.exp(-self.lambda_discount * dist)
        return float(score)

    def run_bundle_building(self):
        """
        Phase 1: Bundle Building.
        Greedily appends tasks to local bundle up to max_bundle_size if the marginal score
        beats the currently recorded highest bid y_ij.
        """
        while len(self.bundle) < self.max_bundle:
            best_task_id = None
            best_marginal_score = -1.0
            best_score_improvement = 0.0
            
            # Current tip position of agent's planned path
            curr_x = self.agent_x
            curr_y = self.agent_y
            if self.path:
                curr_x, curr_y = self.path[-1]
            
            for t_id, t_info in self.known_tasks.items():
                if t_id in self.bundle:
                    continue  # already in our bundle
                
                score = self.calculate_marginal_score(t_info, curr_x, curr_y)
                current_winner_bid = self.winning_bids.get(t_id, 0.0)
                
                # Check if we can beat the current winning bid
                if score > current_winner_bid:
                    improvement = score - current_winner_bid
                    if improvement > best_score_improvement:
                        best_score_improvement = improvement
                        best_marginal_score = score
                        best_task_id = t_id
            
            if best_task_id is not None:
                self.bundle.append(best_task_id)
                t_info = self.known_tasks[best_task_id]
                self.path.append((t_info['x'], t_info['y']))
                self.winning_bids[best_task_id] = best_marginal_score
                self.winning_agents[best_task_id] = self.robot_id
            else:
                break  # No more tasks can be profitably added

    def auction_cycle(self):
        """Periodic auction iteration: builds bundle, publishes bids and peer state."""
        # 1. Run bundle building phase
        self.run_bundle_building()
        
        # 2. Publish current bids to DDS network
        bid_packet = {
            'agent_id': self.robot_id,
            'bids': self.winning_bids,
            'winners': self.winning_agents,
            'bundle': self.bundle,
            'timestamp': time.time()
        }
        msg = String()
        msg.data = json.dumps(bid_packet)
        self.pub_bids.publish(msg)
        
        # 3. Publish local bundle summary
        bundle_msg = String()
        bundle_msg.data = json.dumps({
            'robot_id': self.robot_id,
            'bundle': self.bundle,
            'bundle_count': len(self.bundle),
            'winning_bids': {t: self.winning_bids.get(t, 0.0) for t in self.bundle}
        })
        self.pub_bundle.publish(bundle_msg)
        
        # 4. Optional PeerState broadcast
        if HAVE_CPS_MSGS and self.pub_peer_state is not None:
            ps = PeerState()
            ps.header.stamp = self.get_clock().now().to_msg()
            ps.header.frame_id = 'map'
            ps.robot_id = self.robot_id
            ps.pose.position.x = float(self.agent_x)
            ps.pose.position.y = float(self.agent_y)
            ps.safety_radius_m = 0.5
            if self.path:
                ps.current_goal_position.x = float(self.path[0][0])
                ps.current_goal_position.y = float(self.path[0][1])
            self.pub_peer_state.publish(ps)

    def bids_callback(self, msg: String):
        """
        Phase 2: Consensus Resolution.
        Arbitrates bidding conflicts between peers. If a peer outbids us on a task in our
        bundle, release that task and all subsequent tasks in the bundle.
        """
        try:
            packet = json.loads(msg.data)
            sender = packet.get('agent_id')
            if sender == self.robot_id:
                return
                
            peer_bids = packet.get('bids', {})
            peer_winners = packet.get('winners', {})
            bundle_modified = False
            
            for t_id, bid in peer_bids.items():
                p_winner = peer_winners.get(t_id, sender)
                local_bid = self.winning_bids.get(t_id, -1.0)
                
                # Check if peer has a strictly higher bid
                if bid > local_bid:
                    self.winning_bids[t_id] = float(bid)
                    self.winning_agents[t_id] = p_winner
                    
                    # If this task was in our bundle and won by someone else, release it
                    if t_id in self.bundle and p_winner != self.robot_id:
                        idx = self.bundle.index(t_id)
                        # Release task and all downstream tasks
                        released_tasks = self.bundle[idx:]
                        self.bundle = self.bundle[:idx]
                        self.path = self.path[:idx]
                        bundle_modified = True
                        
                        # Reset bids for released downstream tasks that were claimed by us
                        for rel_t in released_tasks[1:]:
                            if self.winning_agents.get(rel_t) == self.robot_id:
                                self.winning_bids[rel_t] = 0.0
                                self.winning_agents[rel_t] = ''
            
            if bundle_modified:
                # Re-run bundle building immediately with newly available capacity
                self.run_bundle_building()
                
        except Exception as e:
            self.get_logger().warn(f'Error processing peer bid packet: {e}')


def main(args=None):
    rclpy.init(args=args)
    node = CBBAAuctionNode()
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
