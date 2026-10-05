# Maps

`my_map.yaml` is the metadata file for `my_map.pgm`, a saved occupancy-grid image. Nav2's map server reads the YAML, which points to the image and supplies its resolution, origin, and occupancy thresholds.

Use this map with `navy_nav_launch.py`. Generate a replacement only after a successful mapping run, then keep the `.yaml` and `.pgm` together with matching base names.
