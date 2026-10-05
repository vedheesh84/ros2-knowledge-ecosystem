# EmotionDetection.msg - Detected emotion from a face
#
# Published by the emotion_recognizer node for each detected face.
# Used to understand the user's emotional state from facial expressions.

# Detected emotion category
# Values: "neutral", "happy", "sad", "angry", "surprised", "fearful", "disgusted"
string emotion

# Confidence in emotion detection (0.0 to 1.0)
float32 confidence

# ID linking to the face detection this emotion is from
uint32 face_id

# Position of the face in image coordinates (normalized 0-1)
float32 face_center_x
float32 face_center_y

# Secondary emotions with their confidences (optional)
string[] secondary_emotions
float32[] secondary_confidences

# Timestamp
builtin_interfaces/Time stamp
