// Copyright (c) 2024 ROS2 Learning Kit
// MIT License

/**
 * @file arm_hardware_interface.cpp
 * @brief Arm hardware interface implementation
 *
 * LEARNING OBJECTIVES:
 * - See position control hardware implementation
 * - Understand servo angle conversion
 * - Learn arm-specific patterns
 */

#include "mobile_manipulator_hardware/arm_hardware_interface.hpp"

#include <cmath>
#include <sstream>
#include <iomanip>

#include "hardware_interface/types/hardware_interface_type_values.hpp"
#include "rclcpp/rclcpp.hpp"

namespace mobile_manipulator_hardware
{

hardware_interface::CallbackReturn ArmHardwareInterface::on_init(
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

  RCLCPP_INFO(rclcpp::get_logger("ArmHardwareInterface"),
    "Initialized with serial_port=%s, baud=%d",
    serial_port_.c_str(), baud_rate_);

  // Resize vectors for 6 joints
  size_t num_joints = info_.joints.size();
  hw_positions_.resize(num_joints, 0.0);
  hw_velocities_.resize(num_joints, 0.0);
  hw_commands_.resize(num_joints, 0.0);
  prev_positions_.resize(num_joints, 0.0);

  // Configure servo mappings
  // LEARNING: Each joint has different servo ranges and offsets
  servo_configs_.resize(num_joints);

  // Joint 1: Base rotation (-pi to pi) -> servo (0 to 180)
  servo_configs_[0] = {0, -M_PI, M_PI, 0, 180, 90};

  // Joint 2: Shoulder (-pi/2 to pi/2) -> servo (0 to 180)
  servo_configs_[1] = {1, -M_PI/2, M_PI/2, 0, 180, 90};

  // Joint 3: Elbow (-pi/2 to pi/2) -> servo (0 to 180)
  servo_configs_[2] = {2, -M_PI/2, M_PI/2, 0, 180, 90};

  // Joint 4: Wrist pitch (-pi/2 to pi/2) -> servo (0 to 180)
  servo_configs_[3] = {3, -M_PI/2, M_PI/2, 0, 180, 90};

  // Gripper base: Wrist rotation (-pi to pi) -> servo (0 to 180)
  servo_configs_[4] = {4, -M_PI, M_PI, 0, 180, 90};

  // Gripper: Open/close (0 to 1 rad) -> servo (90 to 135)
  servo_configs_[5] = {5, 0, 1.0, 90, 135, 90};

  return hardware_interface::CallbackReturn::SUCCESS;
}

hardware_interface::CallbackReturn ArmHardwareInterface::on_configure(
  const rclcpp_lifecycle::State & /*previous_state*/)
{
  RCLCPP_INFO(rclcpp::get_logger("ArmHardwareInterface"),
    "Configuring: Opening serial port %s", serial_port_.c_str());

  // Create and open serial port
  serial_ = std::make_unique<SerialPort>();
  if (!serial_->open(serial_port_, baud_rate_)) {
    RCLCPP_ERROR(rclcpp::get_logger("ArmHardwareInterface"),
      "Failed to open serial port %s", serial_port_.c_str());
    return hardware_interface::CallbackReturn::ERROR;
  }

  RCLCPP_INFO(rclcpp::get_logger("ArmHardwareInterface"),
    "Serial port opened successfully");

  return hardware_interface::CallbackReturn::SUCCESS;
}

hardware_interface::CallbackReturn ArmHardwareInterface::on_activate(
  const rclcpp_lifecycle::State & /*previous_state*/)
{
  RCLCPP_INFO(rclcpp::get_logger("ArmHardwareInterface"),
    "Activating hardware interface");

  // Reset states
  for (size_t i = 0; i < hw_positions_.size(); ++i) {
    hw_positions_[i] = 0.0;
    hw_velocities_[i] = 0.0;
    hw_commands_[i] = 0.0;
    prev_positions_[i] = 0.0;
  }

  // Flush serial buffer
  if (serial_) {
    serial_->flush();
  }

  return hardware_interface::CallbackReturn::SUCCESS;
}

hardware_interface::CallbackReturn ArmHardwareInterface::on_deactivate(
  const rclcpp_lifecycle::State & /*previous_state*/)
{
  RCLCPP_INFO(rclcpp::get_logger("ArmHardwareInterface"),
    "Deactivating: Moving to home position");

  // Move to home position (all zeros)
  for (size_t i = 0; i < hw_commands_.size(); ++i) {
    hw_commands_[i] = 0.0;
  }
  send_servo_commands();

  return hardware_interface::CallbackReturn::SUCCESS;
}

hardware_interface::CallbackReturn ArmHardwareInterface::on_cleanup(
  const rclcpp_lifecycle::State & /*previous_state*/)
{
  RCLCPP_INFO(rclcpp::get_logger("ArmHardwareInterface"),
    "Cleaning up: Closing serial port");

  if (serial_) {
    serial_->close();
    serial_.reset();
  }

  return hardware_interface::CallbackReturn::SUCCESS;
}

std::vector<hardware_interface::StateInterface>
ArmHardwareInterface::export_state_interfaces()
{
  std::vector<hardware_interface::StateInterface> state_interfaces;

  // Export position and velocity for each joint
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
ArmHardwareInterface::export_command_interfaces()
{
  std::vector<hardware_interface::CommandInterface> command_interfaces;

  // Export position command for each joint
  for (size_t i = 0; i < info_.joints.size(); ++i) {
    command_interfaces.emplace_back(
      hardware_interface::CommandInterface(
        info_.joints[i].name, hardware_interface::HW_IF_POSITION, &hw_commands_[i]));
  }

  return command_interfaces;
}

hardware_interface::return_type ArmHardwareInterface::read(
  const rclcpp::Time & /*time*/, const rclcpp::Duration & period)
{
  if (!serial_ || !serial_->is_open()) {
    return hardware_interface::return_type::ERROR;
  }

  // Read servo position feedback
  std::string line = serial_->read_line();
  if (!line.empty()) {
    parse_servo_feedback(line);
  }

  // Calculate velocities from position changes
  double dt = period.seconds();
  if (dt > 0.0) {
    for (size_t i = 0; i < hw_positions_.size(); ++i) {
      hw_velocities_[i] = (hw_positions_[i] - prev_positions_[i]) / dt;
      prev_positions_[i] = hw_positions_[i];
    }
  }

  return hardware_interface::return_type::OK;
}

hardware_interface::return_type ArmHardwareInterface::write(
  const rclcpp::Time & /*time*/, const rclcpp::Duration & /*period*/)
{
  if (!serial_ || !serial_->is_open()) {
    return hardware_interface::return_type::ERROR;
  }

  send_servo_commands();

  return hardware_interface::return_type::OK;
}

void ArmHardwareInterface::parse_servo_feedback(const std::string & msg)
{
  // Expected format: SERVO_POS,<p1>,<p2>,<p3>,<p4>,<p5>,<p6>
  if (msg.substr(0, 10) != "SERVO_POS,") {
    return;
  }

  std::string data = msg.substr(10);
  std::istringstream iss(data);
  std::string token;
  size_t idx = 0;

  while (std::getline(iss, token, ',') && idx < hw_positions_.size()) {
    try {
      double servo_angle = std::stod(token);
      hw_positions_[idx] = servo_to_joint(idx, servo_angle);
    } catch (...) {
      // Ignore parse errors
    }
    ++idx;
  }
}

void ArmHardwareInterface::send_servo_commands()
{
  if (!serial_ || !serial_->is_open()) {
    return;
  }

  // Format: SET_ALL_SERVOS,<s1>,<s2>,<s3>,<s4>,<s5>,<s6>
  std::ostringstream cmd;
  cmd << std::fixed << std::setprecision(1);
  cmd << "SET_ALL_SERVOS";

  for (size_t i = 0; i < hw_commands_.size(); ++i) {
    double servo_angle = joint_to_servo(i, hw_commands_[i]);
    cmd << "," << servo_angle;
  }
  cmd << "\n";

  serial_->write(cmd.str());
}

double ArmHardwareInterface::joint_to_servo(int joint_idx, double joint_angle)
{
  const auto & config = servo_configs_[joint_idx];

  // Clamp joint angle to limits
  joint_angle = std::max(config.min_angle, std::min(config.max_angle, joint_angle));

  // Linear mapping from joint angle to servo angle
  double ratio = (joint_angle - config.min_angle) / (config.max_angle - config.min_angle);
  double servo_angle = config.min_servo + ratio * (config.max_servo - config.min_servo);

  return servo_angle;
}

double ArmHardwareInterface::servo_to_joint(int joint_idx, double servo_angle)
{
  const auto & config = servo_configs_[joint_idx];

  // Linear mapping from servo angle to joint angle
  double ratio = (servo_angle - config.min_servo) / (config.max_servo - config.min_servo);
  double joint_angle = config.min_angle + ratio * (config.max_angle - config.min_angle);

  return joint_angle;
}

}  // namespace mobile_manipulator_hardware

#include "pluginlib/class_list_macros.hpp"
PLUGINLIB_EXPORT_CLASS(
  mobile_manipulator_hardware::ArmHardwareInterface,
  hardware_interface::SystemInterface)
