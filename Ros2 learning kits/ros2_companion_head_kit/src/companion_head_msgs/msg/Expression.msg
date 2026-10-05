# Expression.msg - Robot facial expression command
#
# Used to command the companion head to display a specific expression.
# The expression_renderer node subscribes to this and updates the face display.

# Expression name (e.g., "happy", "sad", "curious", "neutral", "excited", "sleepy")
string name

# Expression intensity from 0.0 (minimal) to 1.0 (maximum)
float32 intensity 1.0

# Duration for transition from current to target expression (seconds)
float32 transition_duration 0.3

# Optional modifiers (e.g., "blink", "wink_left", "raise_eyebrow")
string[] modifiers

# Timestamp when this expression was requested
builtin_interfaces/Time stamp
