# Mesh Assets

This folder contains STL geometry for vehicle parts: chassis, front wheel, and back wheel. URDF/Xacro files reference these files for realistic visual or collision shape.

Keep filenames stable when replacing a part. If the exported model has a different scale or origin, correct the `<mesh scale>` or the relevant link/joint origin in the URDF.
