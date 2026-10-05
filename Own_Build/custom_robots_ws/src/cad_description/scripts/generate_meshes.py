#!/usr/bin/env python3
"""Generate STL meshes with origins at each link's joint frame."""

import math
import struct
from pathlib import Path

MESH_DIR = Path(__file__).resolve().parent.parent / "meshes"


class STLWriter:
  def __init__(self, name: str):
    self.name = name
    self.triangles = []

  def add_triangle(self, v0, v1, v2):
    ax, ay, az = v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2]
    bx, by, bz = v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2]
    nx = ay * bz - az * by
    ny = az * bx - ax * bz
    nz = ax * by - ay * bx
    length = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
    self.triangles.append(((nx / length, ny / length, nz / length), v0, v1, v2))

  def add_quad(self, v0, v1, v2, v3):
    self.add_triangle(v0, v1, v2)
    self.add_triangle(v0, v2, v3)

  def write(self, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
      header = f"CAD robot mesh: {self.name}".encode("ascii", errors="ignore")
      f.write(header.ljust(80, b"\0")[:80])
      f.write(struct.pack("<I", len(self.triangles)))
      for normal, v0, v1, v2 in self.triangles:
        f.write(struct.pack("<3f", *normal))
        f.write(struct.pack("<3f", *v0))
        f.write(struct.pack("<3f", *v1))
        f.write(struct.pack("<3f", *v2))
        f.write(struct.pack("<H", 0))


def box_mesh(w, sx, sy, sz, ox=0.0, oy=0.0, oz=0.0):
  hx, hy, hz = sx / 2.0, sy / 2.0, sz / 2.0
  corners = [
    (ox - hx, oy - hy, oz - hz), (ox + hx, oy - hy, oz - hz),
    (ox + hx, oy + hy, oz - hz), (ox - hx, oy + hy, oz - hz),
    (ox - hx, oy - hy, oz + hz), (ox + hx, oy - hy, oz + hz),
    (ox + hx, oy + hy, oz + hz), (ox - hx, oy + hy, oz + hz),
  ]
  faces = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (2, 6, 7, 3), (0, 3, 7, 4), (1, 5, 6, 2)]
  for face in faces:
    w.add_quad(*(corners[i] for i in face))


def cylinder_mesh(w, radius, height, segments=32, ox=0.0, oy=0.0, oz=0.0, axis="z"):
  hz = height / 2.0
  if axis == "z":
    bottom = [(ox + radius * math.cos(2 * math.pi * i / segments),
               oy + radius * math.sin(2 * math.pi * i / segments),
               oz - hz) for i in range(segments)]
    top = [(x, y, oz + hz) for x, y, _ in bottom]
  elif axis == "y":
    bottom = [(ox + radius * math.cos(2 * math.pi * i / segments), oy - hz,
               oz + radius * math.sin(2 * math.pi * i / segments)) for i in range(segments)]
    top = [(x, oy + hz, z) for x, _, z in bottom]
  else:
    bottom = [(ox - hz, oy + radius * math.cos(2 * math.pi * i / segments),
               oz + radius * math.sin(2 * math.pi * i / segments)) for i in range(segments)]
    top = [(ox + hz, y, z) for _, y, z in bottom]

  for i in range(segments):
    j = (i + 1) % segments
    w.add_quad(bottom[i], bottom[j], top[j], top[i])
  for i in range(1, segments - 1):
    w.add_triangle(bottom[0], bottom[i], bottom[i + 1])
  for i in range(1, segments - 1):
    w.add_triangle(top[0], top[i + 1], top[i])


def treaded_wheel_mesh(w, radius=0.14, width=0.10, treads=24):
  cylinder_mesh(w, radius * 0.92, width, segments=36, axis="y")
  tread_w = width * 0.18
  tread_h = radius * 0.12
  tread_d = radius * 0.10
  for i in range(treads):
    ang = 2 * math.pi * i / treads
    cx = (radius + tread_d / 2) * math.cos(ang)
    cz = (radius + tread_d / 2) * math.sin(ang)
    box_mesh(w, tread_d, tread_w, tread_h, cx, 0.0, cz)


def coil_spring_mesh(w, radius=0.028, height=0.10, coils=7):
  segments_per_coil = 12
  tube_r = 0.005
  for i in range(coils * segments_per_coil):
    t0 = i / (coils * segments_per_coil)
    t1 = (i + 1) / (coils * segments_per_coil)
    ang0, ang1 = t0 * coils * 2 * math.pi, t1 * coils * 2 * math.pi
    z0, z1 = -t0 * height, -t1 * height
    p0 = (radius * math.cos(ang0), radius * math.sin(ang0), z0)
    p1 = (radius * math.cos(ang1), radius * math.sin(ang1), z1)
    mid = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, (p0[2] + p1[2]) / 2)
    seg_len = math.dist(p0, p1)
    box_mesh(w, tube_r * 2, tube_r * 2, max(seg_len, tube_r * 2), *mid)


def make_base_link():
  w = STLWriter("base_link")
  box_mesh(w, 0.75, 0.55, 0.30, oz=0.15)
  box_mesh(w, 0.68, 0.48, 0.04, oz=0.32)
  box_mesh(w, 0.72, 0.02, 0.22, oy=0.275, oz=0.11)
  box_mesh(w, 0.72, 0.02, 0.22, oy=-0.275, oz=0.11)
  box_mesh(w, 0.02, 0.50, 0.22, ox=0.385, oz=0.15)
  box_mesh(w, 0.02, 0.50, 0.22, ox=-0.385, oz=0.15)
  w.write(MESH_DIR / "base_link.stl")


def make_wheel():
  w = STLWriter("wheel")
  treaded_wheel_mesh(w)
  w.write(MESH_DIR / "wheel.stl")


def make_suspension():
  w = STLWriter("suspension")
  box_mesh(w, 0.06, 0.04, 0.04, oz=-0.02)
  coil_spring_mesh(w)
  box_mesh(w, 0.08, 0.06, 0.03, oz=-0.115)
  w.write(MESH_DIR / "suspension.stl")


def make_lidar():
  w = STLWriter("lidar")
  box_mesh(w, 0.08, 0.08, 0.015, oz=0.007)
  cylinder_mesh(w, 0.055, 0.04, segments=40, oz=0.034)
  cylinder_mesh(w, 0.048, 0.025, segments=40, oz=0.066)
  w.write(MESH_DIR / "lidar.stl")


def make_camera():
  w = STLWriter("camera")
  box_mesh(w, 0.10, 0.04, 0.05, oz=0.025)
  box_mesh(w, 0.06, 0.02, 0.04, oz=0.055)
  cylinder_mesh(w, 0.012, 0.02, segments=20, oz=0.08)
  w.write(MESH_DIR / "camera.stl")


def make_led_strip():
  w = STLWriter("led_strip")
  box_mesh(w, 0.18, 0.015, 0.008)
  w.write(MESH_DIR / "led_strip.stl")


def make_arm_base():
  w = STLWriter("arm_base")
  cylinder_mesh(w, 0.07, 0.06, segments=32, oz=0.03)
  box_mesh(w, 0.12, 0.12, 0.025, oz=0.072)
  w.write(MESH_DIR / "arm_base.stl")


def make_shoulder():
  w = STLWriter("shoulder")
  box_mesh(w, 0.10, 0.12, 0.14, oz=0.07)
  cylinder_mesh(w, 0.045, 0.13, segments=24, axis="x", oz=0.07)
  box_mesh(w, 0.08, 0.06, 0.06, oy=0.10, oz=0.10)
  w.write(MESH_DIR / "shoulder_link.stl")


def make_upper_arm():
  w = STLWriter("upper_arm")
  box_mesh(w, 0.09, 0.09, 0.28, oz=0.14)
  box_mesh(w, 0.04, 0.04, 0.30, oy=0.05, oz=0.15)
  w.write(MESH_DIR / "upper_arm_link.stl")


def make_forearm():
  w = STLWriter("forearm")
  box_mesh(w, 0.075, 0.075, 0.22, oz=0.11)
  box_mesh(w, 0.06, 0.04, 0.05, oy=-0.06, oz=0.12)
  w.write(MESH_DIR / "forearm_link.stl")


def make_wrist():
  w = STLWriter("wrist")
  box_mesh(w, 0.06, 0.08, 0.06, oz=0.03)
  cylinder_mesh(w, 0.035, 0.08, segments=24, axis="x", oz=0.03)
  w.write(MESH_DIR / "wrist_link.stl")


def make_gripper_base():
  w = STLWriter("gripper_base")
  box_mesh(w, 0.08, 0.05, 0.04, oz=0.02)
  box_mesh(w, 0.02, 0.06, 0.03, oz=0.055)
  w.write(MESH_DIR / "gripper_base.stl")


def make_gripper_finger():
  w = STLWriter("gripper_finger")
  box_mesh(w, 0.015, 0.025, 0.06, oz=0.03)
  box_mesh(w, 0.012, 0.018, 0.04, oz=0.08)
  w.write(MESH_DIR / "gripper_finger.stl")


def make_arm_camera():
  w = STLWriter("arm_camera")
  box_mesh(w, 0.05, 0.03, 0.03, oz=0.015)
  cylinder_mesh(w, 0.008, 0.015, segments=16, oz=0.037)
  w.write(MESH_DIR / "arm_camera.stl")


def main():
  make_base_link()
  make_wheel()
  make_suspension()
  make_lidar()
  make_camera()
  make_led_strip()
  make_arm_base()
  make_shoulder()
  make_upper_arm()
  make_forearm()
  make_wrist()
  make_gripper_base()
  make_gripper_finger()
  make_arm_camera()
  print(f"Generated meshes in {MESH_DIR}")


if __name__ == "__main__":
  main()
