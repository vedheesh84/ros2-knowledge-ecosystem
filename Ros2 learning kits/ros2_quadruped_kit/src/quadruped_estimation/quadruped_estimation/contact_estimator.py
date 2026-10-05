#!/usr/bin/env python3
"""
contact_estimator.py - Contact Detection for Quadruped Feet

LEARNING OBJECTIVES:
- Understanding contact detection methods
- Force thresholding for contact
- Why contact matters for state estimation and control

CONTACT DETECTION METHODS:
1. Force sensors (used here): Direct measurement of ground reaction force
2. Position-based: Detect when foot reaches expected ground height
3. Velocity-based: Detect sudden velocity change (impact)
4. Current-based: Motor current spike on contact

WHY CONTACT MATTERS:
- State estimation: Feet in contact provide velocity constraints
- Gait control: Know when to switch from swing to stance
- Force control: Only apply GRF when foot is on ground
- Safety: Detect unexpected contact (collision)

This node simulates force sensor readings based on joint effort.
Real systems would read actual force/torque sensors.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Bool, Float32
from geometry_msgs.msg import WrenchStamped


class ContactEstimator(Node):
    """
    Estimates contact state for each foot.

    In simulation/mock mode:
    - Uses joint efforts as proxy for contact force
    - Thresholds effort to determine contact

    In real hardware:
    - Would read force/torque sensors directly

    Publishes:
    - /contact/{FL,FR,RL,RR}: Bool indicating contact
    - /contact_force/{FL,FR,RL,RR}: Float32 estimated force
    """

    def __init__(self):
        super().__init__('contact_estimator')

        # Parameters
        self.declare_parameter('force_threshold', 10.0)  # N
        self.declare_parameter('debounce_count', 3)  # readings before state change

        self.force_threshold = self.get_parameter('force_threshold').value
        self.debounce_count = self.get_parameter('debounce_count').value

        # Leg names
        self.legs = ['FL', 'FR', 'RL', 'RR']

        # Contact state with debounce
        self.contact_state = {leg: False for leg in self.legs}
        self.contact_count = {leg: 0 for leg in self.legs}

        # Estimated contact forces
        self.contact_force = {leg: 0.0 for leg in self.legs}

        # Joint to leg mapping (KFE joints have most contact info)
        self.kfe_joints = {
            'FL_KFE': 'FL',
            'FR_KFE': 'FR',
            'RL_KFE': 'RL',
            'RR_KFE': 'RR',
        }

        # ==================== SUBSCRIBERS ====================
        self.joint_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_callback,
            10
        )

        # Force sensor subscriptions (if available)
        for leg in self.legs:
            self.create_subscription(
                WrenchStamped,
                f'/force_sensor/{leg}',
                lambda msg, l=leg: self.force_callback(msg, l),
                10
            )

        # ==================== PUBLISHERS ====================
        self.contact_pubs = {}
        self.force_pubs = {}
        for leg in self.legs:
            self.contact_pubs[leg] = self.create_publisher(
                Bool, f'/contact/{leg}', 10)
            self.force_pubs[leg] = self.create_publisher(
                Float32, f'/contact_force/{leg}', 10)

        # Timer for publishing at fixed rate
        self.create_timer(0.01, self.publish_contact)  # 100 Hz

        self.get_logger().info('Contact Estimator initialized')

    def joint_callback(self, msg: JointState):
        """
        Estimate contact from joint efforts.

        In simulation without force sensors, we estimate contact
        by looking at knee joint effort. High effort suggests
        the leg is supporting the robot's weight.
        """
        if not msg.effort:
            return

        # Map joint efforts to legs
        for i, name in enumerate(msg.name):
            if name in self.kfe_joints:
                leg = self.kfe_joints[name]
                effort = abs(msg.effort[i]) if i < len(msg.effort) else 0.0

                # Estimate force from effort (simplified model)
                # Real systems would use proper force sensors
                estimated_force = effort * 3.0  # Approximate scaling

                self.contact_force[leg] = estimated_force
                self.update_contact_state(leg, estimated_force)

    def force_callback(self, msg: WrenchStamped, leg: str):
        """
        Process direct force sensor reading.

        Ground reaction force is primarily in Z direction.
        """
        force_z = abs(msg.wrench.force.z)
        self.contact_force[leg] = force_z
        self.update_contact_state(leg, force_z)

    def update_contact_state(self, leg: str, force: float):
        """
        Update contact state with debouncing.

        Debouncing prevents rapid state changes from noise.
        """
        # Check if force exceeds threshold
        is_contact = force > self.force_threshold

        # Debounce logic
        if is_contact:
            if self.contact_count[leg] < self.debounce_count:
                self.contact_count[leg] += 1
            else:
                self.contact_state[leg] = True
        else:
            if self.contact_count[leg] > 0:
                self.contact_count[leg] -= 1
            else:
                self.contact_state[leg] = False

    def publish_contact(self):
        """Publish contact state and force for all legs."""
        for leg in self.legs:
            # Contact state
            contact_msg = Bool()
            contact_msg.data = self.contact_state[leg]
            self.contact_pubs[leg].publish(contact_msg)

            # Contact force
            force_msg = Float32()
            force_msg.data = self.contact_force[leg]
            self.force_pubs[leg].publish(force_msg)


def main(args=None):
    rclpy.init(args=args)
    node = ContactEstimator()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
