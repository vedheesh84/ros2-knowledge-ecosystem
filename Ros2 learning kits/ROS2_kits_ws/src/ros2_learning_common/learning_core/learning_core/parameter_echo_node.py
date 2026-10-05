#!/usr/bin/env python3
"""
Parameter Echo Node - Understanding ROS2 Parameters
====================================================

LEARNING OBJECTIVES:
--------------------
After studying this node, you will understand:
1. What parameters ARE and why they exist
2. How to declare parameters with default values
3. How to read parameter values
4. How to respond to parameter changes at runtime
5. The difference between parameters and code constants

WHAT ARE PARAMETERS?
--------------------
Parameters are runtime configuration values. They let you change
node behavior WITHOUT modifying code.

    ┌─────────────────────────────────────────────────────────────────┐
    │                   PARAMETERS vs CONSTANTS                       │
    │                                                                 │
    │   CONSTANT (in code):              PARAMETER (configurable):   │
    │   ┌─────────────────────┐          ┌─────────────────────┐     │
    │   │ GREETING = "Hello"  │          │ ros2 param set ...  │     │
    │   │ Requires recompile! │          │ Change at runtime!  │     │
    │   └─────────────────────┘          └─────────────────────┘     │
    │                                                                 │
    └─────────────────────────────────────────────────────────────────┘

Parameters are perfect for:
- Robot-specific settings (wheel diameter, sensor offsets)
- Tuning values (PID gains, thresholds)
- Feature flags (enable_debug, use_simulation)
- File paths (config files, model files)

PARAMETER TYPES:
----------------
ROS2 parameters can be:
- bool: True/False
- int: 42, -17, 0
- float: 3.14, -2.7
- string: "hello", "/path/to/file"
- byte_array: [0x01, 0x02]
- bool_array, int_array, float_array, string_array

PARAMETER LIFECYCLE:
--------------------
1. DECLARE - Tell ROS2 this parameter exists (with default value)
2. GET - Read the current value
3. SET - Change the value (via CLI, launch file, or code)
4. CALLBACK - Optionally respond to changes

USAGE:
------
    # Terminal 1: Run the node
    ros2 run learning_core parameter_echo_node

    # Terminal 2: List parameters
    ros2 param list /parameter_echo

    # Terminal 3: Get a parameter value
    ros2 param get /parameter_echo greeting_message

    # Terminal 4: Set a parameter (and watch the node respond!)
    ros2 param set /parameter_echo greeting_message "Bonjour, ROS2!"

    # Terminal 5: Load from YAML
    ros2 run learning_core parameter_echo_node --ros-args \
        --params-file config/example_params.yaml

TRY THIS:
---------
1. Change the greeting_message and watch the output change
2. Change the echo_rate to speed up or slow down
3. Try changing demo_list and see the array format
4. Load parameters from the YAML file

CHALLENGE:
----------
1. Add a new parameter: echo_count (how many times to echo)
2. Add a boolean parameter: uppercase (convert to uppercase)
3. Add parameter validation (reject invalid values)
"""

import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from rcl_interfaces.msg import SetParametersResult


class ParameterEchoNode(Node):
    """
    A node that demonstrates ROS2 parameter usage.

    This node:
    - Declares several parameters of different types
    - Echoes parameter values periodically
    - Responds to parameter changes in real-time
    """

    def __init__(self):
        """Initialize the parameter echo node."""

        super().__init__('parameter_echo')

        self.get_logger().info('Parameter Echo Node starting...')

        # =====================================================================
        # STEP 1: DECLARE PARAMETERS
        # =====================================================================
        # declare_parameter(name, default_value)
        #
        # IMPORTANT: You MUST declare parameters before using them!
        # This is a safety feature - it prevents typos and documents
        # what parameters the node expects.
        #
        # If you try to get an undeclared parameter, ROS2 will error.

        # String parameter - the message to echo
        self.declare_parameter('greeting_message', 'Hello, ROS2!')

        # Float parameter - how often to echo (in seconds)
        self.declare_parameter('echo_rate', 2.0)

        # Integer parameter - demonstration
        self.declare_parameter('demo_integer', 42)

        # Boolean parameter - demonstration
        self.declare_parameter('demo_bool', True)

        # Array parameter - demonstration
        self.declare_parameter('demo_list', ['apple', 'banana', 'cherry'])

        self.get_logger().info('Parameters declared!')
        self.get_logger().info('Try: ros2 param list /parameter_echo')
        self.get_logger().info('Try: ros2 param set /parameter_echo greeting_message "New message!"')

        # =====================================================================
        # STEP 2: GET INITIAL PARAMETER VALUES
        # =====================================================================
        # get_parameter(name).value returns the current value

        self.greeting = self.get_parameter('greeting_message').value
        self.echo_rate = self.get_parameter('echo_rate').value

        self.get_logger().info(f'Initial greeting: {self.greeting}')
        self.get_logger().info(f'Initial echo rate: {self.echo_rate}s')

        # =====================================================================
        # STEP 3: SET UP PARAMETER CHANGE CALLBACK
        # =====================================================================
        # add_on_set_parameters_callback() registers a function that's
        # called BEFORE parameters change. This lets you:
        # - Validate new values
        # - Reject invalid changes
        # - Update internal state
        #
        # The callback receives a list of Parameter objects and must
        # return a SetParametersResult indicating success or failure.

        self.add_on_set_parameters_callback(self.parameter_callback)

        # =====================================================================
        # STEP 4: CREATE TIMER USING PARAMETER VALUE
        # =====================================================================
        # Note: We use the parameter value for the timer period!
        # This demonstrates using parameters to configure behavior.

        self.timer = self.create_timer(self.echo_rate, self.echo_parameters)

        # Track echo count
        self.echo_count = 0

    def parameter_callback(self, params):
        """
        Called when parameter values are about to change.

        This is where you can:
        - Validate new values
        - Reject invalid changes
        - Update internal state

        Args:
            params: List of Parameter objects being changed

        Returns:
            SetParametersResult: Success/failure with message
        """

        for param in params:
            # Log what's changing
            self.get_logger().info(
                f'Parameter change request: {param.name} = {param.value}'
            )

            # ---- VALIDATE PARAMETERS ----

            if param.name == 'echo_rate':
                # Reject non-positive rates
                if param.value <= 0:
                    return SetParametersResult(
                        successful=False,
                        reason='echo_rate must be positive!'
                    )

                # Update the timer period
                # Note: We need to destroy and recreate the timer
                self.timer.cancel()
                self.timer = self.create_timer(param.value, self.echo_parameters)
                self.echo_rate = param.value
                self.get_logger().info(f'Timer updated to {param.value}s period')

            elif param.name == 'greeting_message':
                # Update internal state
                self.greeting = param.value
                self.get_logger().info(f'Greeting updated to: {param.value}')

            elif param.name == 'demo_integer':
                # Could add validation here
                self.get_logger().info(f'demo_integer set to: {param.value}')

            elif param.name == 'demo_bool':
                self.get_logger().info(f'demo_bool set to: {param.value}')

            elif param.name == 'demo_list':
                self.get_logger().info(f'demo_list set to: {param.value}')

        # Accept the changes
        return SetParametersResult(successful=True)

    def echo_parameters(self):
        """
        Timer callback that echoes current parameter values.

        This demonstrates reading parameters at runtime.
        """

        self.echo_count += 1

        # Get all parameter values
        # Note: For greeting and echo_rate, we use cached values
        # that we update in the callback. For others, we read fresh.

        demo_int = self.get_parameter('demo_integer').value
        demo_bool = self.get_parameter('demo_bool').value
        demo_list = self.get_parameter('demo_list').value

        # Log the values
        self.get_logger().info(f'--- Echo #{self.echo_count} ---')
        self.get_logger().info(f'  greeting_message: {self.greeting}')
        self.get_logger().info(f'  echo_rate: {self.echo_rate}')
        self.get_logger().info(f'  demo_integer: {demo_int}')
        self.get_logger().info(f'  demo_bool: {demo_bool}')
        self.get_logger().info(f'  demo_list: {demo_list}')


def main(args=None):
    """Entry point for the parameter echo node."""

    rclpy.init(args=args)

    node = ParameterEchoNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
