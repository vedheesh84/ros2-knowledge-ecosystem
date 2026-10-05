import math
import numpy as np

class ArmJacobian:
    """Computes Jacobian matrix and manipulability index for arm kinematic chain."""
    def __init__(self, a2=0.12, a3=0.085, d5=0.12):
        self.a2 = a2
        self.a3 = a3
        self.d5 = d5

    def compute_jacobian_planar(self, q2: float, q3: float, q4: float) -> np.ndarray:
        """
        Computes 2x3 planar velocity Jacobian J where [v_r, v_z]^T = J * [dq2, dq3, dq4]^T
        """
        s2 = math.sin(q2)
        c2 = math.cos(q2)
        s23 = math.sin(q2 + q3)
        c23 = math.cos(q2 + q3)
        s234 = math.sin(q2 + q3 + q4)
        c234 = math.cos(q2 + q3 + q4)
        
        J11 = -self.a2 * s2 - self.a3 * s23 - self.d5 * s234
        J12 = -self.a3 * s23 - self.d5 * s234
        J13 = -self.d5 * s234
        
        J21 = self.a2 * c2 + self.a3 * c23 + self.d5 * c234
        J22 = self.a3 * c23 + self.d5 * c234
        J23 = self.d5 * c234
        
        return np.array([[J11, J12, J13],
                         [J21, J22, J23]])

    def manipulability_index(self, q2: float, q3: float, q4: float) -> float:
        """Yoshikawa manipulability measure sqrt(det(J * J^T)). Near 0 indicates singularity."""
        J = self.compute_jacobian_planar(q2, q3, q4)
        JJT = np.dot(J, J.T)
        det = np.linalg.det(JJT)
        return math.sqrt(max(0.0, det))
