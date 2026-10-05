## MM 03: UNIFIED KINEMATIC CHAINS & DYNAMIC MULTI-SENSOR TF TREES

*Purpose: Master spatial coordinate propagation across mobile manipulators. Deconstruct the global-to-tool kinematic chain from map origin to gripper grasp link, trace TF frame composition, understand odometry drift propagation, and resolve spatial transformations.*

### Must Answer
- What is the complete hierarchical TF tree for an autonomous mobile manipulator?
- How does the transformation chain connect `map` $\to$ `odom` $\to$ `base_footprint` $\to$ `camera_optical_frame` $\to$ `arm_base_link` $\to$ `grasp_link`?
- What is the difference between `/tf_static` (fixed robot geometries) and `/tf` (high-frequency dynamic states)?
- How does wheel slip and odometry drift in `odom` propagate through the TF tree to corrupt Cartesian grasping targets?
- How does ROS2 `tf2_ros::Buffer` resolve transforms across different asynchronous sensor timestamps?

### Key Insight
When an object is detected by the camera in `camera_color_optical_frame`, the robot cannot grasp it until that coordinate is projected through the entire dynamic TF tree into the arm's local coordinate frame `arm_base_link`.

---

### 1. The Global Mobile Manipulation TF Tree

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     MOBILE MANIPULATOR TF TREE TOPOLOGY                     │
│                                                                             │
│   [map] (Global Fixed World Frame)                                          │
│     │ (Estimated by AMCL / SLAM at 10-20 Hz)                                │
│     ▼                                                                       │
│   [odom] (Continuous Smooth Local Odometry Frame)                           │
│     │ (Published by EKF / Wheel Encoders + IMU at 50 Hz)                    │
│     ▼                                                                       │
│   [base_footprint] (2D Projection on Floor Plane)                           │
│     │ (Fixed height offset)                                                 │
│     ▼                                                                       │
│   [base_link] (Center of Mass of Mobile Base)                               │
│     │                                                                       │
│     ├──(Fixed)──▶ [laser_frame] (2D LiDAR Scanner)                          │
│     │                                                                       │
│     ├──(Fixed)──▶ [camera_link] ──▶ [camera_color_optical_frame] (Vision)   │
│     │                                                                       │
│     └──(Fixed)──▶ [arm_base_link] (Mounting Pedestal for Robotic Arm)       │
│                     │ (Revolute joint_1 / Base Yaw)                         │
│                     ▼                                                       │
│                   [link_1] ──(joint_2)──▶ [link_2] ──(joint_3)──▶ [link_3]   │
│                                                                      │      │
│                                                                  (joint_4)  │
│                                                                      ▼      │
│                   [grasp_link] (TCP) ◀──(Fixed)── [gripper_base] ◀── [link_4]│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. The Coordinate Transformation Chain

To transform a 3D detected object position ${}^{\text{cam}}\mathbf{p}_{\text{obj}}$ into the arm's base coordinate frame ${}^{\text{arm}}\mathbf{p}_{\text{obj}}$:

$${}^{\text{arm}}\mathbf{p}_{\text{obj}} = \left( {}^{\text{base}} T_{\text{arm}} \right)^{-1} \cdot {}^{\text{base}} T_{\text{cam}} \cdot {}^{\text{cam}}\mathbf{p}_{\text{obj}}$$

Notice that if the camera and arm are both rigidly mounted to `base_link`, the transformation ${}^{\text{arm}} T_{\text{cam}}$ is **completely static** ($/tf\_static$). It does not depend on wheel odometry or world SLAM!

#### The Critical Advantage of Base-Relative Grasping:
By computing grasping targets directly in `base_link` rather than `map`, world-frame SLAM drift and map localization jumps have **zero impact** on grasping accuracy.

---

### 3. Hands-On Lab & Practical Code References

#### 1. Verifying Dynamic Camera-to-Arm Frame Transformation:
```bash
# Launch mobile manipulator display
ros2 launch mobile_manipulator_description display.launch.py

# In another terminal, inspect TF transformation between camera and gripper
ros2 run tf2_ros tf2_echo camera_color_optical_frame grasp_link
```

#### 2. Running Demo 03: Camera TF Projection:
```bash
# Run Demo 03 to observe spatial coordinate transformations
ros2 run mobile_manipulator_demos demo_03_camera_tf.py
```
- Source: [`ros2_mobile_manipulator_kit/src/mobile_manipulator_demos/scripts/demo_03_camera_tf.py`](file:///e:/Intelligent%20Systems%20Knowledge%20Ecosystem/02%20—%20Domains/ROS2/Ros2%20learning%20kits/ros2_mobile_manipulator_kit/src/mobile_manipulator_demos/scripts/demo_03_camera_tf.py)
- Breaker Test: `ros2 run mobile_manipulator_demos break_camera_tf.py`
