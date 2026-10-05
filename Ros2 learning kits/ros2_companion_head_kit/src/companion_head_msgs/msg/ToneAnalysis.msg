# ToneAnalysis.msg - Audio tone/sentiment analysis result
#
# Published by the audio processor when analyzing speech tone.
# Used by mood engine to infer user's emotional state from voice.

# Detected tone category
# Values: "neutral", "happy", "sad", "angry", "excited", "calm", "questioning"
string tone

# Confidence in tone detection (0.0 to 1.0)
float32 confidence

# Audio energy level (0.0 to 1.0, normalized)
float32 energy_level

# Speech rate (words per minute estimate, 0 if not speaking)
float32 speech_rate

# Pitch variation (0.0 = monotone, 1.0 = highly varied)
float32 pitch_variation

# Whether speech was detected in this analysis window
bool speech_detected

# Duration of the analyzed audio segment (seconds)
float32 duration

# Timestamp
builtin_interfaces/Time stamp
