import math
from typing import Optional, Tuple

class InverseKinematics:
    """
    Analytical Inverse Kinematics for 5-DOF Articulated Arm.
    Solves for (q1, q2, q3, q4) given target (x, y, z, pitch).
    """
    def __init__(self, d1=0.096, a2=0.12, a3=0.085, d5=0.12):
        self.d1 = d1
        self.a2 = a2
        self.a3 = a3
        self.d5 = d5
        self.max_reach = a2 + a3 + d5
        self.min_reach = abs(a2 - a3)

    def solve(self, x: float, y: float, z: float, target_pitch: float = -0.5, elbow_up: bool = True) -> Optional[Tuple[float, float, float, float]]:
        """
        Solves IK for target end-effector coordinates.
        Returns:
            Tuple of (q1, q2, q3, q4) in radians, or None if unreachable.
        """
        # 1. Base rotation q1
        q1 = math.atan2(y, x)
        
        # 2. Planar projection in radial plane
        r = math.sqrt(x**2 + y**2)
        
        # 3. Wrist center position (subtract tool length vector)
        rw = r - self.d5 * math.cos(target_pitch)
        zw = z - self.d1 - self.d5 * math.sin(target_pitch)
        
        # Distance from shoulder to wrist
        d_sq = rw**2 + zw**2
        d = math.sqrt(d_sq)
        
        # Reachability check
        if d > (self.a2 + self.a3) or d < abs(self.a2 - self.a3):
            return None  # Target unreachable
            
        # 4. Law of Cosines for elbow joint q3
        cos_q3 = (d_sq - self.a2**2 - self.a3**2) / (2.0 * self.a2 * self.a3)
        cos_q3 = max(-1.0, min(1.0, cos_q3))  # Numerical clamp
        
        if elbow_up:
            q3 = -math.acos(cos_q3)
        else:
            q3 = math.acos(cos_q3)
            
        # 5. Shoulder angle q2
        alpha = math.atan2(zw, rw)
        beta = math.atan2(self.a3 * math.sin(q3), self.a2 + self.a3 * math.cos(q3))
        q2 = alpha - beta
        
        # 6. Wrist pitch q4
        q4 = target_pitch - (q2 + q3)
        
        return q1, q2, q3, q4
