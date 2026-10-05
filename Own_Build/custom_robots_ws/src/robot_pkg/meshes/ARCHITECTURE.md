# Mesh Architecture

Meshes are passive assets. `urdf/` owns their placement and scale; `launch/` only loads the resulting robot description. STL files do not contain ROS joints, physics parameters, topics, or controllers.
