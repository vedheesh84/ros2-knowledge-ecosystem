# Script Architecture

```text
FreeCAD generator ──> meshes/ + urdf/
/cmd_vel ──> propeller spinner ──> /joint_states ──> RViz/Gazebo visual state
```

Both scripts are installed as executable programs by `CMakeLists.txt`, but only the spinner belongs in a running ROS graph.
