# ROS2 Domain — GitHub & Repository System Reference

**Document Status:** Active Operational Reference  
**Repository Name:** `ros2-knowledge-ecosystem`  
**Remote URL:** `git@github.com:vedheesh84/ros2-knowledge-ecosystem.git`  
**Default Branch:** `main`  
**Maintainer / Author:** `vedheesh84 <vedheeshbkr@gmail.com>`  
**Local Path:** `02 — Domains/ROS2` (inside `Intelligent Systems Knowledge Ecosystem`)  
**Parent Workspace:** `/media/ved/DATA/Intelligent Systems Knowledge Ecosystem`  

---

## 1. Purpose & Architectural Context

### Why ROS2 is Maintained as an Independent Repository
The **ROS2 Domain** represents an expansive, production-grade robotics codebase containing:
- 8 specialized ROS2 learning & hardware kits;
- 7 development and simulation workspaces;
- Multiple custom robot URDF/Xacro descriptions and simulation worlds;
- A 25-article canonical curriculum and engineering audit reports.

While it resides physically inside `02 — Domains/ROS2` within the larger **Intelligent Systems Knowledge Ecosystem**, it is intentionally configured as its own **self-contained Git repository**. This architecture ensures:
1. **Separation of Concerns:** Robotics code, build configurations, and launch orchestration are decoupled from founder operations, general venture planning, and other high-level ecosystem notes.
2. **Targeted CI/CD & Testing:** Automated testing (e.g., GitHub Actions running `colcon test`, `ament_flake8`, `ament_cppcheck`, and Gazebo headless simulation tests) can run specifically on robotics packages without triggering on non-code files.
3. **Clean Versioning & Tagging:** Semantic versions and release tags (e.g., `v1.0.0-turtlebot-kit`) apply directly to the robotics stack.
4. **Collaboration & Portability:** The ROS2 codebase can be cloned, shared, or deployed to companion computers (Raspberry Pi, Jetson, PC) without exporting the entire ecosystem.

---

## 2. Repository Structure & Map ("What is What and Where")

The repository is organized into distinct functional layers:

```text
02 — Domains/ROS2/
├── .git/                                   # Git repository root & history
├── .gitignore                              # Comprehensive ROS2/Colcon build exclusion rules
├── README.md                               # Primary domain entry point and collection catalog
├── GITHUB_SYSTEM.md                        # This document: Git/GitHub operational specification
├── KITS_AND_PRODUCTS_STRATEGY.md           # Product philosophy, kit roadmap & hardware specs
├── resources/                              # Architecture frameworks, diagrams, and design docs
│   └── ROS2_Domain_Architecture_Framework.docx
├── ROS2 Articles/                          # 25-article canonical curriculum & knowledge base
│   ├── COMPLETE_INDEX.md                   # Full curriculum navigation & publishing index
│   └── [Article 01 – Article 25]           # Theoretical and hands-on ROS2 publications
├── Ros2 learning kits/                     # 8 Modular Learning & Hardware Kits
│   ├── ROS2_kits_ws/                       # Foundational communications workspace (topics, services, actions)
│   ├── ros2_arm_kit/                       # 5/6-DOF articulated manipulator (MoveIt2, kinematics)
│   ├── ros2_companion_head_kit/            # Affective & social robot (vision, emotion FSM, display)
│   ├── ros2_drone_swarm_kit/               # Multi-agent aerial swarm (consensus, formation flight)
│   ├── ros2_mobile_manipulator_kit/        # 4WD base + 6-DOF arm integration
│   ├── ros2_quadruped_kit/                 # Legged locomotion, balance control & state estimation
│   ├── ros2_reef_drone_kit/                # Underwater AUV (hydrodynamics, DVL & depth fusion)
│   └── ros2_turtlebot_kit/                 # Differential AMR capstone (SLAM Toolbox, Nav2)
├── AMR_ws/                                 # Autonomous Mobile Robot capstone proving ground
│   └── turtlebot3_ws/                      # Industry-standard TurtleBot3 simulation & hardware workspace
├── Distributed_CPS_ws/                     # Multi-tier Cyber-Physical Systems platform
│   └── src/                                # FastDDS Discovery Server, Base Coordinator, CBBA, Map Merger
├── Line_Follower_Evolution_ws/             # 6-Generation evolutionary robotics platform
│   └── src/                                # V1 Reactive -> V6 Exploratory SLAM implementations
├── Mobile_Manipulator_ws/                  # Physical gripper car & Gazebo mobile manipulator workspace
│   └── src/                                # Hardware bridges (YDLidar, Dynamixel, camera), MoveIt, navigation
├── Own_Build/                              # Custom robot builds & engineering assessments
│   ├── cad_description/                   # CAD model imports and robot descriptions
│   ├── spider_pkg/                         # Hexapod/quadruped kinematics and simulation
│   ├── balancing_robot_description/        # Self-balancing two-wheeled robot
│   ├── colcon_ws/ & gazebo_ws/             # Earlier simulation and package experiments
│   └── [AUDIT_REPORTS]                     # Formal engineering assessments of custom builds
├── Robotic_Arm_ws/                         # Articulated arm development & MoveIt2 workspace
├── UAV_ws/                                 # Aerial drone simulation & flight controller workspace
└── AUV_ws/                                 # Historical marine domain exploration workspace
```

### Detailed Breakdown of Components

| Folder / Asset | Category | Description & Purpose |
|---|---|---|
| **`Ros2 learning kits/`** | Product / Educational | Standalone educational robotics platforms covering 8 physical and simulation modalities, complete with step-by-step demos, breakers, and architecture docs. |
| **`AMR_ws/`** | Capstone Workspace | TurtleBot3 proving ground used as the foundational mobile robotics benchmark (Level 1 Capstone). |
| **`Distributed_CPS_ws/`** | Advanced Platform | Production-grade multi-robot cyber-physical coordination system with auction-based task allocation (CBBA), map merging, and Foxglove telemetry bridges. |
| **`Line_Follower_Evolution_ws/`** | Evolutionary System | Demonstrates iterative engineering across 6 generations: reactive bang-bang $\rightarrow$ PID $\rightarrow$ topological graphs $\rightarrow$ full SLAM. |
| **`Mobile_Manipulator_ws/`** | Physical / Simulation | Integrated mobile base + manipulator with real-world hardware interfaces (serial, Dynamixel, LiDAR) and simulation twins. |
| **`Own_Build/`** | Research & Prototyping | Custom robotic platforms (spiders, drones, balancing robots) and rigorous technical audit reports. |
| **`Robotic_Arm_ws/`** | Manipulation | Dedicated manipulator kinematics, trajectory planning, and gripper actuation. |
| **`UAV_ws/`** | Aerial Robotics | Quadcopter dynamics, PX4/SJTU drone models, and aerial navigation launch trees. |
| **`AUV_ws/`** | Marine Robotics | Historical underwater exploration codebase retained for simulation models and hydrodynamic equations. |
| **`ROS2 Articles/`** | Knowledge Base | Canonical technical publications establishing theoretical foundations and practical walkthroughs. |
| **`KITS_AND_PRODUCTS_STRATEGY.md`** | Strategy | Commercial architecture, target audiences, and kit tier taxonomy. |

---

## 3. Git Configuration & Baseline Commit

### 3.1 Initial Commit Baseline
The repository baseline was established on **October 5, 2026**:
* **Commit Hash:** `87d4bb4`
* **Commit Subject:** `feat(ros2): initialize ROS2 Knowledge Ecosystem repository`
* **Scope:** 2,988 tracked files covering all 8 learning kits, active workspaces, CAD models, and curriculum articles.

### 3.2 Git Remote Details
* **Remote Name:** `origin`
* **Fetch URL:** `git@github.com:vedheesh84/ros2-knowledge-ecosystem.git`
* **Push URL:** `git@github.com:vedheesh84/ros2-knowledge-ecosystem.git`

To inspect the configuration locally:
```bash
git -C "/media/ved/DATA/Intelligent Systems Knowledge Ecosystem/02 — Domains/ROS2" remote -v
```

---

## 4. Setting Up Authentication & First Push

### 4.1 SSH Key Authentication (Recommended)
This repository uses the SSH URL (`git@github.com:...`). To verify or configure your SSH access:

1. **Verify SSH Connectivity:**
   ```bash
   ssh -T git@github.com
   ```
   *Expected successful output:* `Hi vedheesh84! You've successfully authenticated, but GitHub does not provide shell access.`

2. **If SSH key is missing or not configured:**
   - Generate a key (if not already existing):
     ```bash
     ssh-keygen -t ed25519 -C "vedheeshbkr@gmail.com"
     ```
   - Copy the public key to clipboard:
     ```bash
     cat ~/.ssh/id_ed25519.pub
     ```
   - Add it to **GitHub Settings $\rightarrow$ SSH and GPG keys $\rightarrow$ New SSH Key**.

### 4.2 GitHub CLI Authentication (`gh`)
If using GitHub CLI tools, refresh your expired session token:
```bash
gh auth login -h github.com
```
Follow the interactive prompt (choose SSH or HTTPS protocol, and authenticate via web browser or personal access token).

### 4.3 Pushing the Initial Commit & Setting Upstream Tracking
To push the initial commit and link the local `main` branch to GitHub:
```bash
cd "/media/ved/DATA/Intelligent Systems Knowledge Ecosystem/02 — Domains/ROS2"
git push -u origin main
```
*The `-u` (or `--set-upstream`) flag links local `main` to `origin/main` so future operations only require `git push` and `git pull`.*

---

## 5. Daily Git Workflow & Operating Standards

Follow this workflow for daily development across any workspace or learning kit:

```text
[Check Status] -> [Branch / Pull] -> [Develop & Test] -> [Colcon Hygiene Check] -> [Stage & Commit] -> [Push]
```

### Step 1: Pre-flight Status Check
Always ensure your working directory is clean and up to date before making changes:
```bash
git status
git pull --rebase origin main
```

### Step 2: Feature Branching (For Significant Work)
For multi-file features, architectural changes, or new kits, create a descriptive branch:
```bash
git checkout -b feat/quadruped-balance-pid
# or for bug fixes:
git checkout -b fix/turtlebot-tf-drift
```

### Step 3: Atomic Staging & Inspection
Never stage blindly with `git add .` without checking status. ROS2 workspaces generate lots of temporary build and log files.
```bash
# Review what changed:
git diff

# Stage specific directories or files:
git add "Ros2 learning kits/ros2_arm_kit/"
# Verify staged contents:
git status
```

### Step 4: Conventional Commits
Write clear, structured commit messages following the **Conventional Commits** standard:

```text
<type>(<scope>): <short imperative description>

[optional body explaining rationale, changes, and consequences]
```

* **Types:**
  - `feat`: A new package, node, robot model, or capability
  - `fix`: Bug fix in launch files, controllers, nodes, or math
  - `docs`: Documentation, READMEs, article updates, or diagrams
  - `refactor`: Code restructuring without behaviour changes
  - `test`: Adding or updating test suites, rostest, or simulation benchmarks
  - `chore`: Build scripts, `.gitignore`, metadata, or package.xml dependency maintenance
* **Scopes:**
  - `(arm)`, `(turtlebot)`, `(quadruped)`, `(reef-drone)`, `(swarm)`, `(companion-head)`, `(mobile-manip)`
  - `(cps)`, `(line-follower)`, `(amr)`, `(own-build)`, `(curriculum)`, `(repo)`
* **Examples:**
  - `feat(quadruped): add inverse kinematics solver for trotting gait`
  - `fix(turtlebot): correct odom to base_footprint transform timestamp`
  - `docs(curriculum): add Article 14 launch orchestration deep-dive`

### Step 5: Push & Synchronize
```bash
git push origin <branch-name>
# Or on main:
git push
```

---

## 6. Robotics-Specific Git Best Practices

Robotics repositories present unique version-control challenges due to heavy build systems, large 3D meshes, sensor logs, and shared environments. Observe the following golden rules:

### Rule 1: Strict Colcon & Build Artifact Exclusion
* **Never commit `build/`, `install/`, or `log/` directories.**
* Committing these directories pollutes Git history with gigabytes of architecture-specific binaries, broken symlinks (`AMENT_CMAKE_SYMLINK_INSTALL`), and timestamped logs.
* The repository `.gitignore` explicitly filters:
  ```gitignore
  build/
  install/
  log/
  COLCON_IGNORE
  ```
* If you ever build inside a subfolder rather than the workspace root, verify that `git status` shows no untracked `build` or `install` artifacts before staging.

### Rule 2: Handling Large Files, Rosbags, and CAD Models
* **Never commit Rosbags:** Recorded `.db3` or `.mcap` bag files can easily exceed several gigabytes. Store bags on external NVMe drives, network storage, or cloud buckets.
* **3D Mesh Optimization:**
  - Keep visual and collision meshes (`.stl`, `.dae`, `.obj`) in `urdf/meshes/` or `description/meshes/`.
  - Ensure meshes are decimated and under 5–10 MB. High-polygon meshes slow down RViz and balloon repository clone sizes.
  - For files exceeding 50 MB, configure [Git LFS](https://git-lfs.github.com/) or host them via external release assets.

### Rule 3: Cross-System Reproducibility
* Always declare dependencies cleanly in `package.xml` and `CMakeLists.txt` / `setup.py`.
* A freshly cloned repository should be buildable by running:
  ```bash
  rosdep install --from-paths src --ignore-src -r -y
  colcon build --symlink-install
  ```
* Do not rely on hardcoded paths (e.g., `/home/ved/...`) in your launch files or source code. Always use `get_package_share_directory('package_name')` or `FindPackageShare`.

### Rule 4: Managing Third-Party Workspaces & Subtrees
* When integrating third-party open-source packages (e.g., TurtleBot3, Nav2, Cartographer), avoid nesting independent `.git` directories directly inside the tree.
* Use ROS `.repos` files (managed via `vcs-tools`) to document upstream sources:
  ```bash
  vcs export src > my_dependencies.repos
  ```
  This allows collaborators to clone third-party packages cleanly without contaminating your own repository history.

### Rule 5: Release Tagging & Milestones
Whenever a robot kit or workspace reaches a stable, tested milestone, tag the commit:
```bash
git tag -a v1.0.0-turtlebot-kit -m "Release v1.0.0: Full Nav2 and SLAM Toolbox Capstone validated"
git push origin v1.0.0-turtlebot-kit
```

---

## 7. Quick Troubleshooting & Maintenance

| Symptom / Error | Root Cause | Solution |
|---|---|---|
| `fatal: not a git repository` | Executed `git` outside `02 — Domains/ROS2` (e.g. in workspace root). | Run commands from within `/media/ved/DATA/Intelligent Systems Knowledge Ecosystem/02 — Domains/ROS2`. |
| `Permission denied (publickey)` | SSH key not loaded or not registered on GitHub. | Run `ssh-add ~/.ssh/id_ed25519` and verify via `ssh -T git@github.com`. |
| `Untracked build/ or install/` | Sub-workspace built without root `.gitignore` coverage. | Ensure `.gitignore` covers subfolder builds or clean via `rm -rf build install log`. |
| `error: failed to push some refs` | Remote contains commits not present locally. | Run `git pull --rebase origin main` before pushing. |
| `Your branch is based on 'origin/main', but the upstream is gone` | Remote branch renamed or upstream not set. | Run `git push -u origin main` to re-bind upstream. |

---

## 8. Summary Checklist for Commits

- [ ] Working directory is clean of `build/`, `install/`, and `log/` files.
- [ ] No large bag files or temporary sensor dumps are staged.
- [ ] Launch files and scripts use relative package lookups, not absolute home paths.
- [ ] Packages compile cleanly with `colcon build`.
- [ ] Commit message follows `type(scope): description` format.
- [ ] Pushed to `origin main` (or dedicated feature branch).

