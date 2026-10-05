# FaceDetectionArray.msg - Array of detected faces
#
# Published by face_detector node containing all faces in current frame.

# Array of detected faces
FaceDetection[] faces

# Total number of faces detected
uint32 count

# Index of the primary/closest face (-1 if none)
int32 primary_face_index

# Image dimensions for reference
uint32 image_width
uint32 image_height

# Timestamp
builtin_interfaces/Time stamp
