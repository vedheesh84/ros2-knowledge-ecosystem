# MoodState.msg - Robot internal emotional state
#
# Represents the companion head's current mood/emotional state.
# Published by the mood_engine node, used by expression and behavior systems.

# Primary mood category
# Values: "neutral", "happy", "sad", "curious", "excited", "sleepy", "confused", "surprised"
string primary_mood

# Continuous mood dimensions (each -1.0 to 1.0 or 0.0 to 1.0)
# Valence: negative to positive (-1.0 = sad, 1.0 = happy)
float32 valence

# Arousal/Energy: calm to excited (0.0 = sleepy, 1.0 = excited)
float32 arousal

# Engagement: how interested the robot is (0.0 = bored, 1.0 = fully engaged)
float32 engagement

# Confidence in the current mood assessment
float32 confidence

# How long the robot has been in this mood (seconds)
float32 duration

# Timestamp
builtin_interfaces/Time stamp
