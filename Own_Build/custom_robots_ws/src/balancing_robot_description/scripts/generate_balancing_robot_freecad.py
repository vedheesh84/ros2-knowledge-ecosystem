#!/usr/bin/env freecadcmd
"""Generate spherical cute self-balancing robot STL meshes and URDF with FreeCAD.

Style: large dark-gray base sphere, light-gray stacked torso cylinders, thin
neck, plain small head (no ears/eyes), yellow power button, fat black wheels.

Run:
  freecadcmd scripts/generate_balancing_robot_freecad.py
"""

from __future__ import annotations

import argparse
import math
import os
from pathlib import Path
import sys

try:
  import FreeCAD as App
  import Mesh
  import Part
except ImportError as exc:
  raise SystemExit(
    "This script must run with FreeCAD Python. Use: "
    "freecadcmd scripts/generate_balancing_robot_freecad.py"
  ) from exc


# ---------------------------------------------------------------------------
# Proportions (meters) — cute kit-scale spherical balance bot
# ---------------------------------------------------------------------------
WHEEL_RADIUS = 0.060
WHEEL_WIDTH = 0.045
TRACK = 0.160
AXLE_Z = WHEEL_RADIUS

BASE_RADIUS = 0.070
BASE_CENTER_Z = BASE_RADIUS

# Stacked light-gray torso rings above the sphere
MID1_RADIUS = 0.055
MID1_HEIGHT = 0.028
MID1_Z = BASE_CENTER_Z + BASE_RADIUS * 0.55 + MID1_HEIGHT / 2.0

MID2_RADIUS = 0.048
MID2_HEIGHT = 0.022
MID2_Z = MID1_Z + MID1_HEIGHT / 2.0 + MID2_HEIGHT / 2.0

MID3_RADIUS = 0.040
MID3_HEIGHT = 0.018
MID3_Z = MID2_Z + MID2_HEIGHT / 2.0 + MID3_HEIGHT / 2.0

NECK_RADIUS = 0.011
NECK_HEIGHT = 0.016
NECK_Z = MID3_Z + MID3_HEIGHT / 2.0 + NECK_HEIGHT / 2.0

HEAD_RADIUS = 0.032
HEAD_CENTER_Z = NECK_Z + NECK_HEIGHT / 2.0 + HEAD_RADIUS * 0.85

EAR_LENGTH = 0.030
EAR_BASE_R = 0.010
EAR_TIP_R = 0.006

VISOR_X = 0.010
VISOR_Y = 0.046
VISOR_Z = 0.012


def package_root() -> Path:
  override = os.environ.get("BALANCING_ROBOT_OUTPUT_ROOT")
  if override:
    return Path(override).expanduser().resolve()

  source_root = Path(__file__).resolve().parent.parent
  if (source_root / "package.xml").exists():
    return source_root

  try:
    from ament_index_python.packages import get_package_share_directory

    return Path(get_package_share_directory("balancing_robot_description")).resolve()
  except Exception:
    return source_root


def centered_box(x, y, z, cx=0.0, cy=0.0, cz=0.0):
  return Part.makeBox(x, y, z, App.Vector(cx - x / 2.0, cy - y / 2.0, cz - z / 2.0))


def centered_cylinder(radius, length, axis="z", cx=0.0, cy=0.0, cz=0.0):
  if axis == "x":
    base = App.Vector(cx - length / 2.0, cy, cz)
    direction = App.Vector(1, 0, 0)
  elif axis == "y":
    base = App.Vector(cx, cy - length / 2.0, cz)
    direction = App.Vector(0, 1, 0)
  else:
    base = App.Vector(cx, cy, cz - length / 2.0)
    direction = App.Vector(0, 0, 1)
  return Part.makeCylinder(radius, length, base, direction)


def centered_sphere(radius, cx=0.0, cy=0.0, cz=0.0):
  return Part.makeSphere(radius, App.Vector(cx, cy, cz))


def centered_cone(radius1, radius2, height, axis="y", cx=0.0, cy=0.0, cz=0.0):
  """Cone along axis; for 'y' it points +Y from cy."""
  if axis == "y":
    cone = Part.makeCone(radius1, radius2, height)
    cone.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), -90.0)
    cone.translate(App.Vector(cx, cy, cz))
    return cone
  if axis == "x":
    cone = Part.makeCone(radius1, radius2, height)
    cone.rotate(App.Vector(0, 0, 0), App.Vector(0, 1, 0), 90.0)
    cone.translate(App.Vector(cx, cy, cz))
    return cone
  cone = Part.makeCone(radius1, radius2, height)
  cone.translate(App.Vector(cx, cy, cz))
  return cone


def fuse_all(shapes):
  fused = shapes[0]
  for shape in shapes[1:]:
    fused = fused.fuse(shape)
  return fused.removeSplitter()


def export_shape(doc, name, shape, mesh_dir: Path):
  obj = doc.addObject("Part::Feature", name)
  obj.Shape = shape
  doc.recompute()
  Mesh.export([obj], str(mesh_dir / f"{name}.stl"))
  doc.removeObject(obj.Name)


def base_sphere_shape():
  return centered_sphere(BASE_RADIUS, cz=BASE_CENTER_Z)


def torso_mid_shape():
  """All light-gray stacked torso rings as one mesh (single color)."""
  r1 = centered_cylinder(MID1_RADIUS, MID1_HEIGHT, cz=MID1_Z)
  r2 = centered_cylinder(MID2_RADIUS, MID2_HEIGHT, cz=MID2_Z)
  r3 = centered_cylinder(MID3_RADIUS, MID3_HEIGHT, cz=MID3_Z)
  return fuse_all([r1, r2, r3])


def torso_upper_shape():
  """Dark collar ring under the neck (thin dark band)."""
  return centered_cylinder(MID3_RADIUS * 0.92, 0.008, cz=MID3_Z + MID3_HEIGHT / 2.0 + 0.003)


def neck_shape():
  return centered_cylinder(NECK_RADIUS, NECK_HEIGHT, cz=NECK_Z)


def head_shape():
  return centered_sphere(HEAD_RADIUS, cz=HEAD_CENTER_Z)


def visor_shape():
  """Yellow visor strip on the front of the head (origin at head center for placement)."""
  strip = centered_box(VISOR_X, VISOR_Y, VISOR_Z, cx=HEAD_RADIUS * 0.72)
  # Slight curve feel via side wedges
  left = centered_box(VISOR_X * 0.7, 0.008, VISOR_Z * 0.85, cx=HEAD_RADIUS * 0.65, cy=VISOR_Y / 2.0)
  right = centered_box(VISOR_X * 0.7, 0.008, VISOR_Z * 0.85, cx=HEAD_RADIUS * 0.65, cy=-(VISOR_Y / 2.0))
  return fuse_all([strip, left, right])


def ear_shape():
  """Black cone ear; local origin at base of cone, extending +Y."""
  return centered_cone(EAR_BASE_R, 0.002, EAR_LENGTH, axis="y", cy=0.0)


def ear_tip_shape():
  """Silver tip sphere; local origin at cone tip."""
  return centered_sphere(EAR_TIP_R)


def power_button_shape():
  """Yellow power-button disc + simple ring (local origin at button center)."""
  disc = centered_cylinder(0.012, 0.004, axis="x")
  ring = centered_cylinder(0.008, 0.005, axis="x")
  # Stem for power symbol feel
  stem = centered_box(0.003, 0.003, 0.010, cx=0.001, cz=0.004)
  return fuse_all([disc, ring, stem])


def accent_bar_shape():
  """Small yellow decorative rectangle."""
  return centered_box(0.006, 0.012, 0.004)


def wheel_shape():
  """Fat black balloon tire with circumferential grooves."""
  tire = centered_cylinder(WHEEL_RADIUS, WHEEL_WIDTH, axis="y")
  outer = centered_cylinder(WHEEL_RADIUS * 0.96, WHEEL_WIDTH * 0.70, axis="y")
  # Rounded balloon shoulders
  shoulder_l = Part.makeTorus(WHEEL_RADIUS * 0.78, WHEEL_WIDTH * 0.22)
  shoulder_l.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), 90.0)
  shoulder_l.translate(App.Vector(0, -WHEEL_WIDTH * 0.15, 0))
  shoulder_r = Part.makeTorus(WHEEL_RADIUS * 0.78, WHEEL_WIDTH * 0.22)
  shoulder_r.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), 90.0)
  shoulder_r.translate(App.Vector(0, WHEEL_WIDTH * 0.15, 0))
  # Groove rings (subtracted look via thinner raised ridges)
  ridges = []
  for i in range(10):
    ang = i * (360.0 / 10.0)
    ridge = centered_box(0.008, WHEEL_WIDTH * 0.55, 0.010, cx=WHEEL_RADIUS * 0.94)
    ridge.rotate(App.Vector(0, 0, 0), App.Vector(0, 1, 0), ang)
    ridges.append(ridge)
  try:
    return fuse_all([tire, outer, shoulder_l, shoulder_r] + ridges)
  except Exception:
    return fuse_all([tire, outer] + ridges)


def write_urdf(urdf_dir: Path):
  urdf_dir.mkdir(parents=True, exist_ok=True)
  pkg = "balancing_robot_description"
  wheel_y = TRACK / 2.0
  wheel_diameter = 2.0 * WHEEL_RADIUS

  # Power button on front of base sphere
  btn_x = BASE_RADIUS * 0.92
  btn_z = BASE_CENTER_Z + 0.01

  # Accent placements on mid torso only (no head/eyes)
  accent_positions = [
    (MID1_RADIUS * 0.95, 0.02, MID1_Z + 0.004),
    (MID1_RADIUS * 0.90, -0.018, MID1_Z - 0.004),
    (MID2_RADIUS * 0.95, 0.012, MID2_Z),
  ]

  accent_visuals = ""
  for ax, ay, az in accent_positions:
    accent_visuals += f"""
    <visual>
      <origin xyz="{ax:.4f} {ay:.4f} {az:.4f}" rpy="0 0 0"/>
      <geometry>
        <mesh filename="package://{pkg}/meshes/accent_bar.stl"/>
      </geometry>
      <material name="accent_yellow"/>
    </visual>"""

  urdf = f"""<?xml version="1.0"?>
<robot name="selfbalance">
  <material name="body_dark">
    <color rgba="0.12 0.38 0.88 1.0"/>
  </material>
  <material name="body_light">
    <color rgba="0.25 0.82 0.90 1.0"/>
  </material>
  <material name="tire_black">
    <color rgba="0.05 0.05 0.06 1.0"/>
  </material>
  <material name="neck_black">
    <color rgba="0.10 0.14 0.22 1.0"/>
  </material>
  <material name="accent_yellow">
    <color rgba="1.0 0.85 0.10 1.0"/>
  </material>

  <link name="base_link">
    <inertial>
      <origin xyz="0 0 {AXLE_Z:.4f}" rpy="0 0 0"/>
      <mass value="1.2"/>
      <inertia ixx="0.004" ixy="0" ixz="0" iyy="0.0045" iyz="0" izz="0.003"/>
    </inertial>

    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <mesh filename="package://{pkg}/meshes/base_sphere.stl"/>
      </geometry>
      <material name="body_dark"/>
    </visual>
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <mesh filename="package://{pkg}/meshes/torso_mid.stl"/>
      </geometry>
      <material name="body_light"/>
    </visual>
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <mesh filename="package://{pkg}/meshes/torso_upper.stl"/>
      </geometry>
      <material name="body_dark"/>
    </visual>
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <mesh filename="package://{pkg}/meshes/neck.stl"/>
      </geometry>
      <material name="neck_black"/>
    </visual>
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <mesh filename="package://{pkg}/meshes/head.stl"/>
      </geometry>
      <material name="body_dark"/>
    </visual>
    <visual>
      <origin xyz="{btn_x:.4f} 0 {btn_z:.4f}" rpy="0 0 0"/>
      <geometry>
        <mesh filename="package://{pkg}/meshes/power_button.stl"/>
      </geometry>
      <material name="accent_yellow"/>
    </visual>
{accent_visuals}

    <collision>
      <origin xyz="0 0 {BASE_CENTER_Z + 0.01:.4f}" rpy="0 0 0"/>
      <geometry>
        <sphere radius="{BASE_RADIUS * 0.82:.4f}"/>
      </geometry>
    </collision>
    <collision>
      <origin xyz="0 0 {MID2_Z:.4f}" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="{MID1_RADIUS:.4f}" length="{MID1_HEIGHT + MID2_HEIGHT + MID3_HEIGHT:.4f}"/>
      </geometry>
    </collision>
    <collision>
      <origin xyz="0 0 {HEAD_CENTER_Z:.4f}" rpy="0 0 0"/>
      <geometry>
        <sphere radius="{HEAD_RADIUS:.4f}"/>
      </geometry>
    </collision>
    <!-- Thin foot keeps two-wheel model upright for manual teleop -->
    <collision>
      <origin xyz="0 0 0.005" rpy="0 0 0"/>
      <geometry>
        <box size="0.08 0.10 0.008"/>
      </geometry>
    </collision>
  </link>

  <link name="left_wheel">
    <inertial>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <mass value="0.12"/>
      <inertia ixx="0.00018" ixy="0" ixz="0" iyy="0.00032" iyz="0" izz="0.00018"/>
    </inertial>
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <mesh filename="package://{pkg}/meshes/wheel.stl"/>
      </geometry>
      <material name="tire_black"/>
    </visual>
    <collision>
      <origin xyz="0 0 0" rpy="1.5708 0 0"/>
      <geometry>
        <cylinder radius="{WHEEL_RADIUS:.4f}" length="{WHEEL_WIDTH:.4f}"/>
      </geometry>
    </collision>
  </link>

  <joint name="left_wheel_joint" type="continuous">
    <parent link="base_link"/>
    <child link="left_wheel"/>
    <origin xyz="0 {wheel_y:.4f} {AXLE_Z:.4f}" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit effort="12" velocity="25"/>
    <dynamics damping="0.1" friction="0.2"/>
  </joint>

  <link name="right_wheel">
    <inertial>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <mass value="0.12"/>
      <inertia ixx="0.00018" ixy="0" ixz="0" iyy="0.00032" iyz="0" izz="0.00018"/>
    </inertial>
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <mesh filename="package://{pkg}/meshes/wheel.stl"/>
      </geometry>
      <material name="tire_black"/>
    </visual>
    <collision>
      <origin xyz="0 0 0" rpy="1.5708 0 0"/>
      <geometry>
        <cylinder radius="{WHEEL_RADIUS:.4f}" length="{WHEEL_WIDTH:.4f}"/>
      </geometry>
    </collision>
  </link>

  <joint name="right_wheel_joint" type="continuous">
    <parent link="base_link"/>
    <child link="right_wheel"/>
    <origin xyz="0 {-wheel_y:.4f} {AXLE_Z:.4f}" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit effort="12" velocity="25"/>
    <dynamics damping="0.1" friction="0.2"/>
  </joint>

  <!-- Gazebo Classic primitive visuals -->
  <gazebo reference="base_link">
    <visual name="gz_base">
      <pose>0 0 {BASE_CENTER_Z:.4f} 0 0 0</pose>
      <geometry><sphere><radius>{BASE_RADIUS:.4f}</radius></sphere></geometry>
      <material>
        <ambient>0.08 0.25 0.65 1</ambient>
        <diffuse>0.12 0.38 0.88 1</diffuse>
        <specular>0.20 0.40 0.80 1</specular>
      </material>
    </visual>
    <visual name="gz_mid1">
      <pose>0 0 {MID1_Z:.4f} 0 0 0</pose>
      <geometry><cylinder><radius>{MID1_RADIUS:.4f}</radius><length>{MID1_HEIGHT:.4f}</length></cylinder></geometry>
      <material>
        <ambient>0.15 0.55 0.65 1</ambient>
        <diffuse>0.25 0.82 0.90 1</diffuse>
        <specular>0.30 0.70 0.80 1</specular>
      </material>
    </visual>
    <visual name="gz_mid2">
      <pose>0 0 {MID2_Z:.4f} 0 0 0</pose>
      <geometry><cylinder><radius>{MID2_RADIUS:.4f}</radius><length>{MID2_HEIGHT:.4f}</length></cylinder></geometry>
      <material>
        <ambient>0.15 0.55 0.65 1</ambient>
        <diffuse>0.25 0.82 0.90 1</diffuse>
        <specular>0.30 0.70 0.80 1</specular>
      </material>
    </visual>
    <visual name="gz_mid3">
      <pose>0 0 {MID3_Z:.4f} 0 0 0</pose>
      <geometry><cylinder><radius>{MID3_RADIUS:.4f}</radius><length>{MID3_HEIGHT:.4f}</length></cylinder></geometry>
      <material>
        <ambient>0.15 0.55 0.65 1</ambient>
        <diffuse>0.25 0.82 0.90 1</diffuse>
        <specular>0.30 0.70 0.80 1</specular>
      </material>
    </visual>
    <visual name="gz_neck">
      <pose>0 0 {NECK_Z:.4f} 0 0 0</pose>
      <geometry><cylinder><radius>{NECK_RADIUS:.4f}</radius><length>{NECK_HEIGHT:.4f}</length></cylinder></geometry>
      <material>
        <ambient>0.08 0.10 0.16 1</ambient>
        <diffuse>0.10 0.14 0.22 1</diffuse>
      </material>
    </visual>
    <visual name="gz_head">
      <pose>0 0 {HEAD_CENTER_Z:.4f} 0 0 0</pose>
      <geometry><sphere><radius>{HEAD_RADIUS:.4f}</radius></sphere></geometry>
      <material>
        <ambient>0.08 0.25 0.65 1</ambient>
        <diffuse>0.12 0.38 0.88 1</diffuse>
        <specular>0.20 0.40 0.80 1</specular>
      </material>
    </visual>
    <visual name="gz_button">
      <pose>{btn_x:.4f} 0 {btn_z:.4f} 0 1.5708 0</pose>
      <geometry><cylinder><radius>0.012</radius><length>0.004</length></cylinder></geometry>
      <material>
        <ambient>0.9 0.75 0.05 1</ambient>
        <diffuse>1.0 0.85 0.10 1</diffuse>
        <emissive>0.5 0.4 0.05 1</emissive>
      </material>
    </visual>
    <material>Gazebo/Blue</material>
  </gazebo>

  <gazebo reference="left_wheel">
    <visual name="gz_wheel">
      <pose>0 0 0 1.5708 0 0</pose>
      <geometry><cylinder><radius>{WHEEL_RADIUS:.4f}</radius><length>{WHEEL_WIDTH:.4f}</length></cylinder></geometry>
      <material>
        <ambient>0.04 0.04 0.04 1</ambient>
        <diffuse>0.06 0.06 0.06 1</diffuse>
      </material>
    </visual>
    <material>Gazebo/Black</material>
    <mu1>2.0</mu1>
    <mu2>2.0</mu2>
    <kp>1e6</kp>
    <kd>100.0</kd>
    <minDepth>0.001</minDepth>
  </gazebo>

  <gazebo reference="right_wheel">
    <visual name="gz_wheel">
      <pose>0 0 0 1.5708 0 0</pose>
      <geometry><cylinder><radius>{WHEEL_RADIUS:.4f}</radius><length>{WHEEL_WIDTH:.4f}</length></cylinder></geometry>
      <material>
        <ambient>0.04 0.04 0.04 1</ambient>
        <diffuse>0.06 0.06 0.06 1</diffuse>
      </material>
    </visual>
    <material>Gazebo/Black</material>
    <mu1>2.0</mu1>
    <mu2>2.0</mu2>
    <kp>1e6</kp>
    <kd>100.0</kd>
    <minDepth>0.001</minDepth>
  </gazebo>

  <gazebo>
    <plugin name="gazebo_ros_joint_state_publisher"
            filename="libgazebo_ros_joint_state_publisher.so">
      <ros>
        <remapping>~/out:=joint_states</remapping>
      </ros>
      <update_rate>50</update_rate>
      <joint_name>left_wheel_joint</joint_name>
      <joint_name>right_wheel_joint</joint_name>
    </plugin>
  </gazebo>

  <gazebo>
    <plugin name="diff_drive" filename="libgazebo_ros_diff_drive.so">
      <ros>
        <remapping>cmd_vel:=cmd_vel</remapping>
        <remapping>odom:=odom</remapping>
      </ros>
      <update_rate>50</update_rate>
      <left_joint>left_wheel_joint</left_joint>
      <right_joint>right_wheel_joint</right_joint>
      <wheel_separation>{TRACK:.4f}</wheel_separation>
      <wheel_diameter>{wheel_diameter:.4f}</wheel_diameter>
      <max_wheel_torque>30</max_wheel_torque>
      <max_wheel_acceleration>8.0</max_wheel_acceleration>
      <publish_odom>true</publish_odom>
      <publish_odom_tf>true</publish_odom_tf>
      <publish_wheel_tf>false</publish_wheel_tf>
      <odometry_frame>odom</odometry_frame>
      <robot_base_frame>base_link</robot_base_frame>
    </plugin>
  </gazebo>
</robot>
"""
  (urdf_dir / "selfbalance.urdf").write_text(urdf, encoding="utf-8")


def generate(output_root: Path):
  mesh_dir = output_root / "meshes"
  urdf_dir = output_root / "urdf"
  mesh_dir.mkdir(parents=True, exist_ok=True)
  urdf_dir.mkdir(parents=True, exist_ok=True)

  # Remove unused / old meshes so install share stays clean
  for stale in (
    "chassis.stl", "pcb.stl", "battery.stl", "motor.stl", "hub.stl",
    "visor.stl", "ear.stl", "ear_tip.stl",
  ):
    stale_path = mesh_dir / stale
    if stale_path.exists():
      stale_path.unlink()

  doc = App.newDocument("selfbalance")
  parts = [
    ("base_sphere", base_sphere_shape()),
    ("torso_mid", torso_mid_shape()),
    ("torso_upper", torso_upper_shape()),
    ("neck", neck_shape()),
    ("head", head_shape()),
    ("power_button", power_button_shape()),
    ("accent_bar", accent_bar_shape()),
    ("wheel", wheel_shape()),
  ]
  for name, shape in parts:
    export_shape(doc, name, shape, mesh_dir)
  App.closeDocument(doc.Name)

  write_urdf(urdf_dir)
  print(f"Generated spherical robot meshes in {mesh_dir}")
  print(f"Generated URDF at {urdf_dir / 'selfbalance.urdf'}")


def main(argv=None):
  argv = list(argv or [])
  if argv and argv[0].endswith(".py"):
    argv = argv[1:]
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument(
    "--output-root",
    type=Path,
    default=package_root(),
    help="Package root or installed share directory to receive meshes/ and urdf/.",
  )
  args = parser.parse_args(argv)
  generate(args.output_root.resolve())


if __name__ == "__main__":
  main(sys.argv[1:])
