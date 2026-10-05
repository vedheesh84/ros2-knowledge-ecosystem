// Copyright (c) 2024 ROS2 Learning Kit
// MIT License

/**
 * @file base_hardware_interface.cpp
 * @brief Mobile base hardware interface implementation
 *
 * LEARNING OBJECTIVES:
 * - See complete ros2_control hardware implementation
 * - Understand lifecycle callback sequence
 * - Learn encoder-to-velocity conversion
 */

#include "mobile_manipulator_hardware/base_hardware_interface.hpp"

#include <cmath>
#include <sstream>
#include <iomanip>

#include "hardware_interface/types/hardware_interface_type_values.hpp"
#include "rclcpp/rclcpp.hpp"

namespace mobile_manipulator_hardware
{

hardware_interface::CallbackReturn BaseHardwareInterface::on_init(
  const hardware_interface::HardwareInfo & info)
{
  // Call parent
  if (hardware_interface::SystemInterface::on_init(info) !=
      hardware_interface::CallbackReturn::SUCCESS)
  {
    return hardware_interface::CallbackReturn::ERROR;
  }

  // Parse parameters from URDF
  serial_port_ = info_.hardware_parameters["serial_port"];
  baud_rate_ = std::stoi(info_.hardware_parameters["baud_rate"]);
  wheel_radius_ = std::stod(info_.hardware_parameters["wheel_radius"]);
  wheel_separation_ = std::stod(info_.hardware_parameters["wheel_separation"]);
  encoder_cpr_ = std::stoi(info_.hardware_parameters["encoder_cpr"]);

  RCLCPP_INFO(rclcpp::get_logger("BaseHardwareInterface"),
    "Initialized with serial_port=%s, baud=%d, wheel_radius=%.3f",
    serial_port_.c_str(), baud_rate_, wheel_radius_);

  // Resize vectors for 4 wheels
  hw_positions_.resize(4, 0.0);
  hw_velocities_.resize(4, 0.0);
  hw_commands_.resize(4, 0.0);
  encoder_counts_.resize(4, 0);
  prev_encoder_counts_.resize(4, 0);

  return hardware_interface::CallbackReturn::SUCCESS;
}

hardware_interface::CallbackReturn BaseHardwareInterface::on_configure(
  const rclcpp_lifecycle::State & /*previous_state*/)
{
  RCLCPP_INFO(rclcpp::get_logger("BaseHardwareInterface"),
    "Configuring: Opening serial port %s", serial_port_.c_str());

  // Create and open serial port
  serial_ = std::make_unique<SerialPort>();
  if (!serial_->open(serial_port_, baud_rate_)) {
    RCLCPP_ERROR(rclcpp::get_logger("BaseHardwareInterface"),
      "Failed to open serial port %s", serial_port_.c_str());
    return hardware_interface::CallbackReturn::ERROR;
  }

  RCLCPP_INFO(rclcpp::get_logger("BaseHardwareInterface"),
    "Serial port opened successfully");

  return hardware_interface::CallbackReturn::SUCCESS;
}

hardware_interface::CallbackReturn BaseHardwareInterface::on_activate(
  const rclcpp_lifecycle::State & /*previous_state*/)
{
  RCLCPP_INFO(rclcpp::get_logger("BaseHardwareInterface"),
    "Activating hardware interface");

  // Reset states
  for (size_t i = 0; i < 4; ++i) {
    hw_positions_[i] = 0.0;
    hw_velocities_[i] = 0.0;
    hw_commands_[i] = 0.0;
    encoder_counts_[i] = 0;
    prev_encoder_counts_[i] = 0;
  }

  // Flush serial buffer
  if (serial_) {
    serial_->flush();
  }

  return hardware_interface::CallbackReturn::SUCCESS;
}

hardware_interface::CallbackReturn BaseHardwareInterface::on_deactivate(
  const rclcpp_lifecycle::State & /*previous_state*/)
{
  RCLCPP_INFO(rclcpp::get_logger("BaseHardwareInterface"),
    "Deactivating: Stopping motors");

  // Stop motors
  for (size_t i = 0; i < 4; ++i) {
    hw_commands_[i] = 0.0;
  }
  send_velocity_command();

  return hardware_interface::CallbackReturn::SUCCESS;
}

hardware_interface::CallbackReturn BaseHardwareInterface::on_cleanup(
  const rclcpp_lifecycle::State & /*previous_state*/)
{
  RCLCPP_INFO(rclcpp::get_logger("BaseHardwareInterface"),
    "Cleaning up: Closing serial port");

  if (serial_) {
    serial_->close();
    serial_.reset();
  }

  return hardware_interface::CallbackReturn::SUCCESS;
}

std::vector<hardware_interface::StateInterface>
BaseHardwareInterface::export_state_interfaces()
{
  std::vector<hardware_interface::StateInterface> state_interfaces;

  // Export position and velocity for each wheel
  for (size_t i = 0; i < info_.joints.size(); ++i) {
    state_interfaces.emplace_back(
      hardware_interface::StateInterface(
        info_.joints[i].name, hardware_interface::HW_IF_POSITION, &hw_positions_[i]));

    state_interfaces.emplace_back(
      hardware_interface::StateInterface(
        info_.joints[i].name, hardware_interface::HW_IF_VELOCITY, &hw_velocities_[i]));
  }

  return state_interfaces;
}

std::vector<hardware_interface::CommandInterface>
BaseHardwareInterface::export_command_interfaces()
{
  std::vector<hardware_interface::CommandInterface> command_interfaces;

  // Export velocity command for each wheel
  for (size_t i = 0; i < info_.joints.size(); ++i) {
    command_interfaces.emplace_back(
      hardware_interface::CommandInterface(
        info_.joints[i].name, hardware_interface::HW_IF_VELOCITY, &hw_commands_[i]));
  }

  return command_interfaces;
}

hardware_interface::return_type BaseHardwareInterface::read(
  const rclcpp::Time & /*time*/, const rclcpp::Duration & period)
{
  if (!serial_ || !serial_->is_open()) {
    return hardware_interface::return_type::ERROR;
  }

  // Read encoder feedback from serial
  std::string line = serial_->read_line();
  if (!line.empty()) {
    parse_encoder_message(line);
  }

  // Calculate velocities from encoder counts
  double dt = period.seconds();
  if (dt > 0.0) {
    for (size_t i = 0; i < 4; ++i) {
      int64_t delta = encoder_counts_[i] - prev_encoder_counts_[i];
      prev_encoder_counts_[i] = encoder_counts_[i];

      // Convert encoder counts to radians
      double delta_rad = (2.0 * M_PI * delta) / encoder_cpr_;
      hw_positions_[i] += delta_rad;
      hw_velocities_[i] = delta_rad / dt;
    }
  }

  return hardware_interface::return_type::OK;
}

hardware_interface::return_type BaseHardwareInterface::write(
  const rclcpp::Time & /*time*/, const rclcpp::Duration & /*period*/)
{
  if (!serial_ || !serial_->is_open()) {
    return hardware_interface::return_type::ERROR;
  }

  send_velocity_command();

  return hardware_interface::return_type::OK;
}

void BaseHardwareInterface::parse_encoder_message(const std::string & msg)
{
  // Expected format: ENC,<fl>,<fr>,<bl>,<br>
  if (msg.substr(0, 4) != "ENC,") {
    return;
  }

  std::string data = msg.substr(4);
  std::istringstream iss(data);
  std::string token;
  size_t idx = 0;

  while (std::getline(iss, token, ',') && idx < 4) {
    try {
      encoder_counts_[idx] = std::stoll(token);
    } catch (...) {
      // Ignore parse errors
    }
    ++idx;
  }
}

void BaseHardwareInterface::send_velocity_command()
{
  if (!serial_ || !serial_->is_open()) {
    return;
  }

  // Convert wheel velocities (rad/s) to linear velocities (m/s)
  // For diff drive, we average left and right wheels
  double left_vel = (hw_commands_[0] + hw_commands_[2]) / 2.0 * wheel_radius_;
  double right_vel = (hw_commands_[1] + hw_commands_[3]) / 2.0 * wheel_radius_;

  // Format: VEL,<left>,<right>
  std::ostringstream cmd;
  cmd << std::fixed << std::setprecision(3);
  cmd << "VEL," << left_vel << "," << right_vel << "\n";

  serial_->write(cmd.str());
}

}  // namespace mobile_manipulator_hardware

#include "pluginlib/class_list_macros.hpp"
PLUGINLIB_EXPORT_CLASS(
  mobile_manipulator_hardware::BaseHardwareInterface,
  hardware_interface::SystemInterface)
