#!/usr/bin/env freecadcmd
"""Generate the drone STL meshes and URDF with FreeCAD.

Run from the source package with:
  freecadcmd scripts/generate_drone_freecad.py

After installation, this can also be run with:
  ros2 run drone_pkg generate_drone_freecad.py
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

try:
  import FreeCAD as App
  import Mesh
  import Part
except ImportError as exc:
  raise SystemExit(
    "This script must run with FreeCAD Python. Use: freecadcmd scripts/generate_drone_freecad.py"
  ) from exc


def package_root() -> Path:
  override = os.environ.get("DRONE_PKG_OUTPUT_ROOT")
  if override:
    return Path(override).expanduser().resolve()

  source_root = Path(__file__).resolve().parent.parent
  if (source_root / "package.xml").exists():
    return source_root

  try:
    from ament_index_python.packages import get_package_share_directory

    return Path(get_package_share_directory("drone_pkg")).resolve()
  except Exception:
    return source_root


def centered_box(x: float, y: float, z: float, cx: float = 0.0, cy: float = 0.0, cz: float = 0.0):
  return Part.makeBox(x, y, z, App.Vector(cx - (x / 2.0), cy - (y / 2.0), cz - (z / 2.0)))


def centered_cylinder(radius: float, length: float, axis: str = "z", cx: float = 0.0, cy: float = 0.0, cz: float = 0.0):
  if axis == "x":
    base = App.Vector(cx - (length / 2.0), cy, cz)
    direction = App.Vector(1, 0, 0)
  elif axis == "y":
    base = App.Vector(cx, cy - (length / 2.0), cz)
    direction = App.Vector(0, 1, 0)
  else:
    base = App.Vector(cx, cy, cz - (length / 2.0))
    direction = App.Vector(0, 0, 1)
  return Part.makeCylinder(radius, length, base, direction)


def fuse_all(shapes):
  fused = shapes[0]
  for shape in shapes[1:]:
    fused = fused.fuse(shape)
  return fused.removeSplitter()


def export_shape(doc, name: str, shape, mesh_dir: Path):
  obj = doc.addObject("Part::Feature", name)
  obj.Shape = shape
  doc.recompute()
  Mesh.export([obj], str(mesh_dir / f"{name}.stl"))
  doc.removeObject(obj.Name)


def body_shape():
  return fuse_all([
    centered_box(0.46, 0.22, 0.10, cz=0.00),
    centered_box(0.30, 0.16, 0.045, cz=0.072),
    centered_box(0.12, 0.14, 0.07, cx=0.25, cz=0.005),
    centered_box(0.08, 0.18, 0.035, cx=-0.25, cz=-0.015),
  ])


def arm_x_shape():
  return fuse_all([
    centered_box(0.92, 0.045, 0.035, cz=0.015),
    centered_box(0.18, 0.065, 0.025, cx=0.30, cz=0.04),
    centered_box(0.18, 0.065, 0.025, cx=-0.30, cz=0.04),
  ])


def arm_y_shape():
  return fuse_all([
    centered_box(0.045, 0.92, 0.035, cz=0.015),
    centered_box(0.065, 0.18, 0.025, cy=0.30, cz=0.04),
    centered_box(0.065, 0.18, 0.025, cy=-0.30, cz=0.04),
  ])


def motor_hub_shape():
  return fuse_all([
    centered_cylinder(0.055, 0.055, axis="z", cz=0.0),
    centered_cylinder(0.035, 0.045, axis="z", cz=0.050),
  ])


def propeller_shape():
  return fuse_all([
    centered_cylinder(0.025, 0.012, axis="z", cz=0.0),
    centered_box(0.30, 0.030, 0.006, cz=0.004),
    centered_box(0.030, 0.30, 0.006, cz=0.004),
    centered_box(0.11, 0.045, 0.008, cx=0.095, cz=0.007),
    centered_box(0.11, 0.045, 0.008, cx=-0.095, cz=0.007),
    centered_box(0.045, 0.11, 0.008, cy=0.095, cz=0.007),
    centered_box(0.045, 0.11, 0.008, cy=-0.095, cz=0.007),
  ])


def landing_skid_shape():
  return fuse_all([
    centered_cylinder(0.012, 0.52, axis="x", cz=-0.18),
    centered_box(0.018, 0.018, 0.18, cx=0.18, cz=-0.09),
    centered_box(0.018, 0.018, 0.18, cx=-0.18, cz=-0.09),
    centered_box(0.38, 0.016, 0.018, cz=0.00),
  ])


def camera_block_shape():
  return fuse_all([
    centered_box(0.09, 0.06, 0.055, cx=0.0, cz=0.0),
    centered_cylinder(0.018, 0.020, axis="x", cx=0.055, cz=0.002),
    centered_box(0.035, 0.04, 0.030, cx=-0.060, cz=0.0),
  ])


def write_urdf(urdf_dir: Path):
  urdf_dir.mkdir(parents=True, exist_ok=True)
  prop_joints = "\n".join([
    f"""  <link name=\"{name}_propeller\">
    <inertial>
      <origin xyz=\"0 0 0\" rpy=\"0 0 0\"/>
      <mass value=\"0.02\"/>
      <inertia ixx=\"1e-5\" ixy=\"0\" ixz=\"0\" iyy=\"1e-5\" iyz=\"0\" izz=\"2e-5\"/>
    </inertial>
    <visual>
      <geometry>
        <mesh filename=\"package://drone_pkg/meshes/propeller.stl\"/>
      </geometry>
      <material name=\"propeller_orange\"/>
    </visual>
    <collision>
      <origin xyz=\"0 0 0\" rpy=\"0 0 0\"/>
      <geometry>
        <cylinder radius=\"0.16\" length=\"0.02\"/>
      </geometry>
    </collision>
  </link>
  <joint name=\"{name}_propeller_joint\" type=\"continuous\">
    <parent link=\"base_link\"/>
    <child link=\"{name}_propeller\"/>
    <origin xyz=\"{x} {y} 0.105\" rpy=\"0 0 0\"/>
    <axis xyz=\"0 0 1\"/>
  </joint>"""
    for name, x, y in [
      ("front_left", "0.32", "0.32"),
      ("front_right", "0.32", "-0.32"),
      ("rear_left", "-0.32", "0.32"),
      ("rear_right", "-0.32", "-0.32"),
    ]
  ])

  motor_visuals = "\n".join([
    f"""    <visual>
      <origin xyz=\"{x} {y} 0.075\" rpy=\"0 0 0\"/>
      <geometry>
        <mesh filename=\"package://drone_pkg/meshes/motor_hub.stl\"/>
      </geometry>
      <material name=\"motor_black\"/>
    </visual>
    <collision>
      <origin xyz=\"{x} {y} 0.075\" rpy=\"0 0 0\"/>
      <geometry>
        <cylinder radius=\"0.06\" length=\"0.09\"/>
      </geometry>
    </collision>"""
    for x, y in [
      ("0.32", "0.32"),
      ("0.32", "-0.32"),
      ("-0.32", "0.32"),
      ("-0.32", "-0.32"),
    ]
  ])

  gazebo_link_settings = "\n".join([
    f"""  <gazebo reference=\"{link}\">
    <gravity>false</gravity>
    {"    <kinematic>true</kinematic>" if link != "base_link" else ""}
    <visual>
      <material>
        <ambient>{ambient}</ambient>
        <diffuse>{diffuse}</diffuse>
      </material>
    </visual>
    <material>{material}</material>
  </gazebo>"""
    for link, material, ambient, diffuse in [
      ("base_link", "Gazebo/Blue", "0.05 0.20 0.70 1.0", "0.12 0.40 0.95 1.0"),
      ("front_left_propeller", "Gazebo/Orange", "0.70 0.30 0.02 1.0", "0.95 0.45 0.05 1.0"),
      ("front_right_propeller", "Gazebo/Orange", "0.70 0.30 0.02 1.0", "0.95 0.45 0.05 1.0"),
      ("rear_left_propeller", "Gazebo/Orange", "0.70 0.30 0.02 1.0", "0.95 0.45 0.05 1.0"),
      ("rear_right_propeller", "Gazebo/Orange", "0.70 0.30 0.02 1.0", "0.95 0.45 0.05 1.0"),
    ]
  ])
  # Clean accidental blank lines for base_link
  gazebo_link_settings = gazebo_link_settings.replace("\n\n    <visual>", "\n    <visual>")

  urdf = f"""<?xml version=\"1.0\"?>
<robot name=\"freecad_drone\">
  <material name=\"body_blue\">
    <color rgba=\"0.12 0.40 0.95 1.0\"/>
  </material>
  <material name=\"arm_dark\">
    <color rgba=\"0.12 0.12 0.14 1.0\"/>
  </material>
  <material name=\"motor_black\">
    <color rgba=\"0.05 0.05 0.06 1.0\"/>
  </material>
  <material name=\"propeller_orange\">
    <color rgba=\"0.95 0.45 0.05 1.0\"/>
  </material>
  <material name=\"skid_silver\">
    <color rgba=\"0.82 0.82 0.86 1.0\"/>
  </material>
  <material name=\"camera_yellow\">
    <color rgba=\"0.95 0.82 0.12 1.0\"/>
  </material>

  <link name=\"base_link\">
    <inertial>
      <origin xyz=\"0 0 0\" rpy=\"0 0 0\"/>
      <mass value=\"1.8\"/>
      <inertia ixx=\"0.05\" ixy=\"0\" ixz=\"0\" iyy=\"0.05\" iyz=\"0\" izz=\"0.08\"/>
    </inertial>
    <visual>
      <origin xyz=\"0 0 0\" rpy=\"0 0 0\"/>
      <geometry>
        <mesh filename=\"package://drone_pkg/meshes/body.stl\"/>
      </geometry>
      <material name=\"body_blue\"/>
    </visual>
    <visual>
      <origin xyz=\"0 0 0\" rpy=\"0 0 0\"/>
      <geometry>
        <mesh filename=\"package://drone_pkg/meshes/arm_x.stl\"/>
      </geometry>
      <material name=\"arm_dark\"/>
    </visual>
    <visual>
      <origin xyz=\"0 0 0\" rpy=\"0 0 0\"/>
      <geometry>
        <mesh filename=\"package://drone_pkg/meshes/arm_y.stl\"/>
      </geometry>
      <material name=\"arm_dark\"/>
    </visual>
{motor_visuals}
    <visual>
      <origin xyz=\"0 0.16 -0.08\" rpy=\"0 0 0\"/>
      <geometry>
        <mesh filename=\"package://drone_pkg/meshes/landing_skid.stl\"/>
      </geometry>
      <material name=\"skid_silver\"/>
    </visual>
    <visual>
      <origin xyz=\"0 -0.16 -0.08\" rpy=\"0 0 0\"/>
      <geometry>
        <mesh filename=\"package://drone_pkg/meshes/landing_skid.stl\"/>
      </geometry>
      <material name=\"skid_silver\"/>
    </visual>
    <visual>
      <origin xyz=\"0.29 0 -0.02\" rpy=\"0 0 0\"/>
      <geometry>
        <mesh filename=\"package://drone_pkg/meshes/camera_block.stl\"/>
      </geometry>
      <material name=\"camera_yellow\"/>
    </visual>
    <collision>
      <origin xyz=\"0 0 0\" rpy=\"0 0 0\"/>
      <geometry>
        <box size=\"0.50 0.24 0.14\"/>
      </geometry>
    </collision>
    <collision>
      <origin xyz=\"0 0 0.015\" rpy=\"0 0 0\"/>
      <geometry>
        <box size=\"0.95 0.08 0.06\"/>
      </geometry>
    </collision>
    <collision>
      <origin xyz=\"0 0 0.015\" rpy=\"0 0 0\"/>
      <geometry>
        <box size=\"0.08 0.95 0.06\"/>
      </geometry>
    </collision>
  </link>

{prop_joints}

{gazebo_link_settings}

  <gazebo>
    <plugin name=\"gazebo_ros_joint_pose_trajectory\" filename=\"libgazebo_ros_joint_pose_trajectory.so\">
      <ros></ros>
      <update_rate>50</update_rate>
    </plugin>
  </gazebo>
</robot>
"""
  (urdf_dir / "drone.urdf").write_text(urdf, encoding="utf-8")


def generate(output_root: Path):
  mesh_dir = output_root / "meshes"
  urdf_dir = output_root / "urdf"
  mesh_dir.mkdir(parents=True, exist_ok=True)
  urdf_dir.mkdir(parents=True, exist_ok=True)

  doc = App.newDocument("freecad_drone")
  for name, shape in [
    ("body", body_shape()),
    ("arm_x", arm_x_shape()),
    ("arm_y", arm_y_shape()),
    ("motor_hub", motor_hub_shape()),
    ("propeller", propeller_shape()),
    ("landing_skid", landing_skid_shape()),
    ("camera_block", camera_block_shape()),
  ]:
    export_shape(doc, name, shape, mesh_dir)
  App.closeDocument(doc.Name)

  write_urdf(urdf_dir)
  print(f"Generated FreeCAD drone meshes in {mesh_dir}")
  print(f"Generated URDF at {urdf_dir / 'drone.urdf'}")


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
