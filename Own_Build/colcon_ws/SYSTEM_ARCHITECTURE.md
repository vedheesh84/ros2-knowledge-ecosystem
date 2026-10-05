# colcon_ws - System Architecture

## Package Overview

| Package | Layer | Purpose |
|---------|-------|---------|
| `cex_pkg` | Educational | ROS2 fundamentals (pub/sub, services, actions) |
| `rviz_tutorial` | Visualization | URDF models, RViz configs, Gazebo integration |
| `slam_toolbox_src` | Perception | SLAM configuration for 2D laser mapping |
| `nav2_src` | Planning/Control | Navigation2 stack configuration |
| `cartographer_src` | Perception | Google Cartographer SLAM (alternative) |
| `gazebo_src` | Simulation | Gazebo world files and spawn configs |
| `package_test` | System | Empty template package |

---

## 1. Package-by-Package Analysis

### cex_pkg (Educational Layer)

**Purpose:** Demonstrates core ROS2 concepts through practical examples

**Nodes:**
| Node | Type | Responsibility |
|------|------|----------------|
| `simple_publisher` | Publisher | Publishes String messages on `/chatter` |
| `simple_subscriber` | Subscriber | Listens to `/chatter` topic |
| `simple_pub_sub` | Pub/Sub | Single node that publishes AND subscribes |
| `publish_two_numbers` | Publisher | Publishes custom NumPair messages |
| `add_two_int_srv` | Service Server | AddTwoInt service (a + b = sum) |
| `add_two_ints_client` | Service Client | Calls AddTwoInt with CLI args |
| `teleport_action_server` | Action Server | MoveTurtle action for turtlesim |
| `move_turtle_client` | Action Client | Sends MoveTurtle goals |
| `move_turtle` | Publisher | Publishes Twist to turtle1/cmd_vel |
| `subscriber_client_node` | Subscriber+Client | Subscribes NumPair, calls service |

**Custom Interfaces:**
```yaml
NumPair.msg:
  int64 a
  int64 b

AddTwoInt.srv:
  REQUEST: int64 a, int64 b
  RESPONSE: int64 sum

MoveTurtle.action:
  GOAL: float32 x, float32 y
  RESULT: bool success
  FEEDBACK: float32 distance_moved
```

**Topics:**
| Topic | Type | Publisher | Subscriber |
|-------|------|-----------|------------|
| `/chatter` | String/NumPair | simple_publisher, pub_two_num | simple_subscriber, sub_client_add |
| `/turtle1/cmd_vel` | Twist | move_turtle | turtlesim |

**Services:**
- `/add_two_int` (AddTwoInt)

**Actions:**
- `/move_turtle` (MoveTurtle)

---

### rviz_tutorial (Visualization Layer)

**Purpose:** URDF models, RViz configs, simulation launch

**Robot Model (robot.urdf.xacro):**
```
3-wheel differential drive robot
├── Base Link: 30cm × 20cm × 10cm (3kg)
├── Right/Left Wheels: 4.25cm radius, continuous joints
├── Center Spherical Wheel: passive caster
├── Lidar sensor (included via lidar.xacro)
└── Camera sensor (included via camera.xacro)
```

**Gazebo Diff Drive Plugin:**
- Wheel separation: 0.22m
- Max torque: 5.0 Nm
- Max acceleration: 10.0 m/s²
- Publishes: `/odom`, wheel TF transforms

**Launch Files:**
- `urdf_rviz.launch.py` - Basic URDF visualization
- `demo.launch.py` - Interactive joint control GUI
- `simple_car_spawn_full.launch.py` - Gazebo + robot spawn
- `Q_slam_launch.py` - Nav2 SLAM pattern
- `Q_navigation_launch.py` - Full Nav2 stack
- `Q_localization_launch.py` - AMCL localization

---

### slam_toolbox_src (Perception Layer)

**Purpose:** 2D laser-based SLAM/localization

**Topics:**
| Topic | Type | Direction | Purpose |
|-------|------|-----------|---------|
| `/scan` | LaserScan | Subscribe | Laser input |
| `/map` | OccupancyGrid | Publish | Generated map |
| `/tf` | Transform | Pub/Sub | Frame transforms |

**Services:**
- `/slam_toolbox/serialize_map` - Save map to file
- `/slam_toolbox/deserialize_map` - Load map from file

**Key Parameters (mapping_params.yaml):**
```yaml
solver: CeresSolver
resolution: 0.05 m/cell
max_laser_range: 20.0 m
minimum_travel_distance: 0.5 m
minimum_travel_heading: 0.5 rad
do_loop_closing: true
```

---

### nav2_src (Planning/Control Layer)

**Purpose:** Navigation2 stack for autonomous navigation

**Nodes (Lifecycle Managed):**
| Node | Purpose |
|------|---------|
| `map_server` | Static map provider |
| `amcl` | Particle filter localization |
| `planner_server` | Global path planning (NavFn) |
| `controller_server` | Local planning (DWB) |
| `bt_navigator` | Behavior tree orchestration |
| `waypoint_follower` | Waypoint navigation |
| `behavior_server` | Recovery behaviors |
| `velocity_smoother` | Velocity filtering |

**Topics:**
| Topic | Type | Purpose |
|-------|------|---------|
| `/map` | OccupancyGrid | Static map |
| `/scan` | LaserScan | Obstacle detection |
| `/cmd_vel` | Twist | Velocity commands |
| `/odom` | Odometry | Robot odometry |
| `/goal_pose` | PoseStamped | Navigation goal |

**Actions:**
- `/navigate_to_pose` (NavigateToPose)
- `/navigate_through_poses` (NavigateThroughPoses)
- `/follow_path` (FollowPath)
- `/spin`, `/backup`, `/wait` (Recovery)

**Key Parameters:**
```yaml
Controller (DWB):
  max_vel_x: 0.26 m/s
  max_vel_theta: 1.0 rad/s
  acc_lim_x: 2.5 m/s²

Costmaps:
  resolution: 0.05 m/cell
  inflation_radius: 0.55 m
  robot_radius: 0.22 m
```

---

### cartographer_src (Perception Layer - Alternative)

**Purpose:** Google Cartographer SLAM configuration

**Launch:** `cartographer_SimpleCar.launch.py`
- Uses `turtlebot3_lds_2d.lua` configuration
- Resolution: 0.05 m/cell

---

### gazebo_src (Simulation Layer)

**Purpose:** Gazebo world files and spawn configurations

**Launch Files:**
- `gazebo_world.launch.py` - Spawns robot in cafe_world
- `gazebo_turtleworld.launch.py` - TurtleBot3 world

---

## 2. System Architecture Analysis

### Layered Architecture

```
VISUALIZATION & SIMULATION LAYER
├── rviz_tutorial (URDF, RViz, visualization)
├── gazebo_src (Gazebo worlds)
└── package_test (template)

PERCEPTION LAYER
├── slam_toolbox_src (Laser SLAM/Localization)
└── cartographer_src (Alternative SLAM)

PLANNING & CONTROL LAYER
├── nav2_src (Navigation2 stack)
└── cex_pkg (Educational control examples)

EDUCATIONAL LAYER
└── cex_pkg (ROS2 fundamentals)
```

### Data Flow

```
HARDWARE INPUTS:
  Lidar → /scan
  Odometry encoder → /odom

PERCEPTION PIPELINE:
  /scan → slam_toolbox_src (mapping/localization)
              ↓
          /map, /tf, /pose

NAVIGATION PIPELINE:
  Goal → nav2_src/bt_navigator
            ├─→ planner_server (/map) → path
            ├─→ controller_server
            └─→ /cmd_vel

SIMULATION:
  /cmd_vel → gazebo_src (physics)
              ├─→ /odom
              └─→ /scan
```

---

## 3. Coordination Patterns

### Lifecycle Management (Nav2)

```
lifecycle_manager coordinates:
1. map_server (loads static map)
2. amcl (initializes particle filter)
3. planner_server (loads planner plugins)
4. controller_server (loads controller plugins)
5. bt_navigator (loads BT plugins)
```

### Service-Based Communication (cex_pkg)

```
pub_two_num → NumPair topic
               ↓
            sub_client_add (subscriber)
               ↓
            Filters for condition (a % 2 == 0)
               ↓
            AddTwoInt service call (async)
```

---

## 4. Coupling Analysis

### Tight Coupling

| Coupling | Risk |
|----------|------|
| Frame names (map, odom, base_link) | Wrong names cause lookup failures |
| Scan topic (/scan) | Wrong topic breaks SLAM |
| Nav2 ↔ TF chain | Missing transform causes failure |

### Loose Coupling

| Component | Why Loose |
|-----------|-----------|
| Costmap plugins | Plugin architecture |
| Planner/Controller | YAML configuration |
| SLAM modes | Launch parameter selection |

---

## 5. Reusability Analysis

### Highly Reusable

| Component | Reason |
|-----------|--------|
| URDF/Xacro patterns | Standard structure |
| Nav2 parameter files | Standard configuration |
| Message definitions (cex_pkg) | Importable |
| Launch file patterns | Composable |

### Robot-Specific

| Component | Reason |
|-----------|--------|
| Wheel separation values | Physical robot |
| Controller gains | Tuned for dynamics |
| Sensor positions | Robot geometry |

---

## 6. Topic Summary

| Topic | Publisher | Subscriber | Type |
|-------|-----------|------------|------|
| `/scan` | Gazebo/Lidar | SLAM, Navigation | LaserScan |
| `/map` | SLAM Toolbox | Navigation, RViz | OccupancyGrid |
| `/odom` | Gazebo diff drive | Navigation, RViz | Odometry |
| `/tf` | SLAM, RSP, Gazebo | Navigation, RViz | TFMessage |
| `/cmd_vel` | Navigation | Gazebo controller | Twist |
| `/goal_pose` | User/Application | BT Navigator | PoseStamped |
| `/chatter` | cex_pkg examples | cex_pkg examples | String |

---

## 7. Parameter Summary

| Node | Key Parameters |
|------|----------------|
| SLAM Toolbox | `resolution`, `minimum_travel_distance`, `do_loop_closing` |
| Nav2 Controller | `max_vel_x`, `max_vel_theta`, `acc_lim_*`, goal tolerances |
| Costmaps | `resolution`, `inflation_radius`, `robot_radius` |
| Diff Drive Plugin | `wheel_separation`, `wheel_diameter`, `max_wheel_torque` |

---

## 8. Integration Complexity Hotspots

| Hotspot | Issue | Mitigation |
|---------|-------|------------|
| TF chain | Any break causes system failure | view_frames debugging |
| Startup timing | Race conditions | TimerActions with delays |
| Frame IDs | Wrong names cause lookup failures | Consistent naming |
| Covariance tuning | Poor fusion if wrong | Careful parameter tuning |

