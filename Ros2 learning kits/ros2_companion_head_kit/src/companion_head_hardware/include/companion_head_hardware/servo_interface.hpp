// Copyright (c) 2024 ROS2 Learning Kit
// MIT License

#ifndef COMPANION_HEAD_HARDWARE__SERVO_INTERFACE_HPP_
#define COMPANION_HEAD_HARDWARE__SERVO_INTERFACE_HPP_

#include <memory>
#include <string>
#include <vector>

#include "hardware_interface/system_interface.hpp"
#include "hardware_interface/handle.hpp"
#include "hardware_interface/hardware_info.hpp"
#include "hardware_interface/types/hardware_interface_return_values.hpp"
#include "rclcpp_lifecycle/state.hpp"
#include "rclcpp/macros.hpp"

#include "companion_head_hardware/serial_port.hpp"

namespace companion_head_hardware
{

class ServoInterface : public hardware_interface::SystemInterface
{
public:
  RCLCPP_SMART_PTR_DEFINITIONS(ServoInterface)

  hardware_interface::CallbackReturn on_init(
    const hardware_interface::HardwareInfo & info) override;

  hardware_interface::CallbackReturn on_configure(
    const rclcpp_lifecycle::State & previous_state) override;

  hardware_interface::CallbackReturn on_cleanup(
    const rclcpp_lifecycle::State & previous_state) override;

  hardware_interface::CallbackReturn on_activate(
    const rclcpp_lifecycle::State & previous_state) override;

  hardware_interface::CallbackReturn on_deactivate(
    const rclcpp_lifecycle::State & previous_state) override;

  std::vector<hardware_interface::StateInterface> export_state_interfaces() override;

  std::vector<hardware_interface::CommandInterface> export_command_interfaces() override;

  hardware_interface::return_type read(
    const rclcpp::Time & time, const rclcpp::Duration & period) override;

  hardware_interface::return_type write(
    const rclcpp::Time & time, const rclcpp::Duration & period) override;

private:
  std::string serial_port_;
  int baud_rate_;
  std::unique_ptr<SerialPort> serial_;

  // Joint states and commands
  // Index 0: neck_pan_joint, Index 1: neck_tilt_joint
  std::vector<double> hw_positions_;
  std::vector<double> hw_velocities_;
  std::vector<double> hw_commands_;
  std::vector<double> prev_positions_;

  void parse_feedback(const std::string & msg);
  void send_commands();
  double rad_to_deg(double rad) const;
  double deg_to_rad(double deg) const;
};

}  // namespace companion_head_hardware

#endif  // COMPANION_HEAD_HARDWARE__SERVO_INTERFACE_HPP_
