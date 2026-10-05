# FaceDetection.msg - Single detected face
#
# Published by face_detector node for each face found in the camera image.

# Unique ID for tracking this face across frames
uint32 id

# Bounding box in image coordinates (pixels)
uint32 bbox_x
uint32 bbox_y
uint32 bbox_width
uint32 bbox_height

# Normalized center position (0.0 to 1.0)
float32 center_x
float32 center_y

# Estimated 3D position relative to camera (meters)
# Only valid if depth information is available
geometry_msgs/Point position

# Detection confidence (0.0 to 1.0)
float32 confidence

# Whether this face is being tracked from previous frame
bool is_tracked

# Number of consecutive frames this face has been tracked
uint32 track_count

# Timestamp
builtin_interfaces/Time stamp
