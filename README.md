# ROS2

## Role in the ecosystem

ROS2 is an established technical foundation for the ecosystem’s robotics and intelligent-systems work. It provides practical experience in computation graphs, interfaces, launch orchestration, TF, simulation, control, navigation, perception, manipulation, and system integration.

This domain folder currently preserves existing documentation without adapting it to the new standards. Its immediate purpose is orientation and classification.

## Product & Kit Strategy

The robotics kit ecosystem is structured around a deliberate product philosophy: **"Don't sell a pile of components. Sell a path into intelligent robotics."**

For full portfolio architecture, intelligence dimensions, and hardware/software specifications, refer to [Kits & Products Strategy](KITS_AND_PRODUCTS_STRATEGY.md).

## Repository & Version Control Architecture

This domain is maintained as an independent Git repository (`ros2-knowledge-ecosystem`) connected to GitHub at `git@github.com:vedheesh84/ros2-knowledge-ecosystem.git`.

For the complete repository directory map, operational workflows, commit conventions, and robotics-specific GitHub practices, refer to [GitHub & Repository System Reference](GITHUB_SYSTEM.md).

## Collection map

Refer to [ROS2 Domain Architecture Framework](resources/ROS2_Domain_Architecture_Framework.docx) for historical structure and navigation details.

| Collection | Classification | Current status | Notes |
|---|---|---|---|
| [ROS2_kits_ws](<Ros2 learning kits/ROS2_kits_ws/README.md>) | Learning resource | Established reference | Core ROS2 learning workspace, learning map, glossary, and package-level lessons. |
| [ros2_arm_kit](<Ros2 learning kits/ros2_arm_kit/README.md>) | Learning system | Established reference / Product | 5/6-DOF articulated robotic arm for kinematics, precision control, and MoveIt2 manipulation. |
| [Robotic_Arm_ws](<Robotic_Arm_ws/README.md>) | Manipulation workspace | Established reference | Development and experimentation workspace for articulated robotic arms. |
| [ros2_turtlebot_kit](<Ros2 learning kits/ros2_turtlebot_kit/README.md>) | Learning system | Established reference | Mobile-robot learning foundation (AMR, SLAM, Nav2). |
| [ros2_mobile_manipulator_kit](<Ros2 learning kits/ros2_mobile_manipulator_kit/README.md>) | Learning system | Established reference | Manipulation, perception, TF, and coordination learning material. |
| [ros2_quadruped_kit](<Ros2 learning kits/ros2_quadruped_kit/README.md>) | Learning system | Established reference | Legged locomotion, estimation, control, and integration learning material. |
| [ros2_reef_drone_kit](<Ros2 learning kits/ros2_reef_drone_kit/README.md>) | Learning system | Established reference | Underwater robotics, sensor fusion, control, and navigation learning material. |
| [ros2_companion_head_kit](<Ros2 learning kits/ros2_companion_head_kit/README.md>) | Learning system | Established reference / Product | Social & affective robotics platform with gaze tracking, face display, and emotion FSM. |
| [ros2_drone_swarm_kit](<Ros2 learning kits/ros2_drone_swarm_kit/README.md>) | Learning system | Established reference / Product | Multi-agent aerial drone swarm platform for distributed consensus and formation flight. |
| [UAV_ws](<UAV_ws/README.md>) | Aerial swarm workspace | Established reference | Development and experimentation workspace for aerial drones and swarm coordination. |
| [Mobile_Manipulator_ws](<Mobile_Manipulator_ws/README.md>) | Mobile manipulation domain | Established reference / Production | Comprehensive 4WD + 6-DOF arm mobile manipulator domain with physical hardware and Gazebo simulation. |
| [Distributed_CPS_ws](<Distributed_CPS_ws/README.md>) | Multi-tier CPS platform | Active workspace & products | Distributed multi-robot CPS platform with FastDDS Discovery Server, Base Coordinator, Map Merger, CBBA, and Foxglove telemetry. |
| [Line_Follower_Evolution_ws](<Line_Follower_Evolution_ws/README.md>) | 4-Generation evolutionary platform | Active workspace & products | Complete Line Follower Evolution (V1 Reactive -> V2-V3 Stabilized Dynamics -> V4-V5 Topological Graph Navigation -> V6 Exploratory SLAM). |
| [Own_Build](<Own_Build/README.md>) | Custom robot models & assessments | Active workspace & audits | Custom multi-robot models (`spider_pkg`, `drone_pkg`, `cad_description`, `balancing_robot_description`, `robot_pkg`) and engineering assessment reports. |
| [gazebo_ws](<Own_Build/gazebo_ws/SYSTEM_ARCHITECTURE.md>) | Historical experiment | Historical | Earlier robot and simulator experiments. |
| [colcon_ws](<Own_Build/colcon_ws/SYSTEM_ARCHITECTURE.md>) | Historical experiment | Historical | Earlier package, navigation, mapping, and simulation experiments. |
| [turtlebot3_ws](<AMR_ws/turtlebot3_ws/README.md>) | Embodied Capstone System | Established Reference / Capstone | Industry-standard TurtleBot3 mobile robotics platform serving as the Level 1 Capstone proving ground. |
| AUV_ws | Historical experiment | Historical | Retained as earlier marine domain exploration material. |

These statuses are organisation labels, not technical evaluations. They should be updated if a collection becomes active again.

## ROS2 Articles

The [ROS2 Articles](<ROS2 Articles/COMPLETE_INDEX.md>) are the canonical technical reference and publishing source for the 25-article curriculum. The articles connect conceptual explanations directly to practical examples, demonstrations, and implementations across the ROS2 learning-kit range.

The publishing-facing location under Founder Operations is a pointer to this canonical source, not a second article collection.

## Relationships

- ROS2 contributes practical foundations to Robotics and future Cyber-Physical Systems work.
- ROS2 learning kits provide demonstrations and implementation context for the ROS2 Articles.
- Sensor systems, perception, AI/ML, and distributed intelligence build on ROS2 where it is useful, without being limited to ROS2.
