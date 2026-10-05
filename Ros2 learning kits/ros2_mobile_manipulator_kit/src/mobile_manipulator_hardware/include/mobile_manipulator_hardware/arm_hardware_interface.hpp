// Copyright (c) 2024 ROS2 Learning Kit
// MIT License

#ifndef MOBILE_MANIPULATOR_HARDWARE__ARM_HARDWARE_INTERFACE_HPP_
#define MOBILE_MANIPULATOR_HARDWARE__ARM_HARDWARE_INTERFACE_HPP_

/**
 * @file arm_hardware_interface.hpp
 * @brief ros2_control hardware interface for manipulator arm
 *
 * LEARNING OBJECTIVES:
 * - Understand position control interface
 * - See servo communication patterns
 * - Learn arm-specific hardware abstraction
 *
 * SERIAL PROTOCOL:
 *   Commands sent: SET_ALL_SERVOS,<s1>,<s2>,<s3>,<s4>,<s5>,<s6>\n
 *   Feedback received: SERVO_POS,<p1>,<p2>,<p3>,<p4>,<p5>,<p6>\n
 *
 * JOINTS:
 *   0: joint_1 (base rotation)
 *   1: joint_2 (shoulder)
 *   2: joint_3 (elbow)
 *   3: joint_4 (wrist pitch)
 *   4: gripper_base_joint (wrist rotation)
 *   5: left_gear_joint (gripper)
 */

#include <memory>
#include <string>
#include <vector>

#include "hardware_interface/handle.hpp"
#include "hardware_interface/hardware_info.hpp"
#include "hardware_interface/system_interface.hpp"
#include "hardware_interface/types/hardware_interface_return_values.hpp"
#include "rclcpp/macros.hpp"
#include "rclcpp_lifecycle/state.hpp"

#include "mobile_manipulator_hardware/serial_port.hpp"

namespace mobile_manipulator_hardware
{

class ArmHardwareInterface : public hardware_interface::SystemInterface
{
public:
  RCLCPP_SHARED_PTR_DEFINITIONS(ArmHardwareInterface)

  // Lifecycle callbacks
  hardware_interface::CallbackReturn on_init(
    const hardware_interface::HardwareInfo & info) override;

  hardware_interface::CallbackReturn on_configure(
    const rclcpp_lifecycle::State & previous_state) override;

  hardware_interface::CallbackReturn on_activate(
    const rclcpp_lifecycle::State & previous_state) override;

  hardware_interface::CallbackReturn on_deactivate(
    const rclcpp_lifecycle::State & previous_state) override;

  hardware_interface::CallbackReturn on_cleanup(
    const rclcpp_lifecycle::State & previous_state) override;

  // Interface exports
  std::vector<hardware_interface::StateInterface> export_state_interfaces() override;
  std::vector<hardware_interface::CommandInterface> export_command_interfaces() override;

  // Read/write
  hardware_interface::return_type read(
    const rclcpp::Time & time, const rclcpp::Duration & period) override;

  hardware_interface::return_type write(
    const rclcpp::Time & time, const rclcpp::Duration & period) override;

private:
  // Serial communication
  std::unique_ptr<SerialPort> serial_;
  std::string serial_port_;
  int baud_rate_;

  // Joint states (6 joints: 5 arm + 1 gripper)
  std::vector<double> hw_positions_;
  std::vector<double> hw_velocities_;
  std::vector<double> hw_commands_;

  // Previous positions for velocity calculation
  std::vector<double> prev_positions_;

  // Servo mapping (joint angle to servo angle)
  struct ServoConfig {
    int channel;
    double min_angle;    // radians
    double max_angle;    // radians
    double min_servo;    // servo degrees (0-180)
    double max_servo;    // servo degrees (0-180)
    double offset;       // servo center offset
  };
  std::vector<ServoConfig> servo_configs_;

  // Helper methods
  void parse_servo_feedback(const std::string & msg);
  void send_servo_commands();
  double joint_to_servo(int joint_idx, double joint_angle);
  double servo_to_joint(int joint_idx, double servo_angle);
};

}  // namespace mobile_manipulator_hardware

#endif  // MOBILE_MANIPULATOR_HARDWARE__ARM_HARDWARE_INTERFACE_HPP_
