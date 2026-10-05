import math
import numpy as np

class ForwardKinematics:
    """
    Analytical Forward Kinematics for 5-DOF Articulated Arm.
    
    Link Lengths (meters):
      d1: Base to shoulder height (0.096 m)
      a2: Upper arm length (0.12 m)
      a3: Forearm length (0.085 m)
      d5: Wrist to tool tip / grasp point (0.12 m)
    """
    def __init__(self, d1=0.096, a2=0.12, a3=0.085, d5=0.12):
        self.d1 = d1
        self.a2 = a2
        self.a3 = a3
        self.d5 = d5

    def compute_fk(self, q1, q2, q3, q4=0.0, q_wrist=0.0):
        """
        Compute End-Effector Position and Orientation from joint angles (radians).
        Returns:
            (x, y, z, pitch_angle)
        """
        # Planar reach in arm plane
        r = self.a2 * math.cos(q2) + self.a3 * math.cos(q2 + q3) + self.d5 * math.cos(q2 + q3 + q4)
        z = self.d1 + self.a2 * math.sin(q2) + self.a3 * math.sin(q2 + q3) + self.d5 * math.sin(q2 + q3 + q4)
        
        # 3D Cartesian coordinates
        x = r * math.cos(q1)
        y = r * math.sin(q1)
        pitch = q2 + q3 + q4
        
        return x, y, z, pitch

    def compute_link_positions(self, q1, q2, q3):
        """Returns 3D positions of all key joint frames for visualization."""
        p0 = np.array([0.0, 0.0, 0.0])
        p1 = np.array([0.0, 0.0, self.d1])
        
        r2 = self.a2 * math.cos(q2)
        p2 = np.array([r2 * math.cos(q1), r2 * math.sin(q1), self.d1 + self.a2 * math.sin(q2)])
        
        r3 = r2 + self.a3 * math.cos(q2 + q3)
        p3 = np.array([r3 * math.cos(q1), r3 * math.sin(q1), self.d1 + self.a2 * math.sin(q2) + self.a3 * math.sin(q2 + q3)])
        
        return p0, p1, p2, p3
