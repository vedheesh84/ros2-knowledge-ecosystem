// Copyright (c) 2024 ROS2 Learning Kit
// MIT License

#ifndef MOBILE_MANIPULATOR_HARDWARE__BASE_HARDWARE_INTERFACE_HPP_
#define MOBILE_MANIPULATOR_HARDWARE__BASE_HARDWARE_INTERFACE_HPP_

/**
 * @file base_hardware_interface.hpp
 * @brief ros2_control hardware interface for mobile base
 *
 * LEARNING OBJECTIVES:
 * - Understand hardware_interface::SystemInterface
 * - See lifecycle callbacks in C++
 * - Learn velocity command/state interfaces
 *
 * SERIAL PROTOCOL:
 *   Commands sent: VEL,<left_vel>,<right_vel>\n
 *   Feedback received: ENC,<fl>,<fr>,<bl>,<br>\n
 *
 * ARCHITECTURE:
 *   diff_drive_controller
 *         |
 *         v
 *   Command Interfaces (velocity)
 *         |
 *         v
 *   BaseHardwareInterface
 *         |
 *         v
 *   Serial -> Arduino
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

class BaseHardwareInterface : public hardware_interface::SystemInterface
{
public:
  RCLCPP_SHARED_PTR_DEFINITIONS(BaseHardwareInterface)

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

  // Robot parameters
  double wheel_radius_;
  double wheel_separation_;
  int encoder_cpr_;

  // Joint states (4 wheels)
  std::vector<double> hw_positions_;
  std::vector<double> hw_velocities_;
  std::vector<double> hw_commands_;

  // Encoder tracking
  std::vector<int64_t> encoder_counts_;
  std::vector<int64_t> prev_encoder_counts_;

  // Helper methods
  void parse_encoder_message(const std::string & msg);
  void send_velocity_command();
};

}  // namespace mobile_manipulator_hardware

#endif  // MOBILE_MANIPULATOR_HARDWARE__BASE_HARDWARE_INTERFACE_HPP_
