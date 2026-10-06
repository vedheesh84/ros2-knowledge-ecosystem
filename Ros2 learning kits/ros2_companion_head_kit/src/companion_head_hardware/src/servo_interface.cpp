// Copyright (c) 2024 ROS2 Learning Kit
// MIT License

#include "companion_head_hardware/servo_interface.hpp"

#include <cmath>
#include <sstream>
#include <iomanip>
#include <algorithm>

#include "hardware_interface/types/hardware_interface_type_values.hpp"
#include "rclcpp/rclcpp.hpp"

namespace companion_head_hardware
{

hardware_interface::CallbackReturn ServoInterface::on_init(
  const hardware_interface::HardwareInfo & info)
{
  if (hardware_interface::SystemInterface::on_init(info) !=
      hardware_interface::CallbackReturn::SUCCESS)
  {
    return hardware_interface::CallbackReturn::ERROR;
  }

  // Parse parameters
  if (info_.hardware_parameters.find("serial_port") != info_.hardware_parameters.end()) {
    serial_port_ = info_.hardware_parameters.at("serial_port");
  } else {
    serial_port_ = "/dev/ttyUSB0";
  }

  if (info_.hardware_parameters.find("baud_rate") != info_.hardware_parameters.end()) {
    baud_rate_ = std::stoi(info_.hardware_parameters.at("baud_rate"));
  } else {
    baud_rate_ = 115200;
  }

  RCLCPP_INFO(rclcpp::get_logger("CompanionHeadServoInterface"),
    "Initialized with serial_port=%s, baud=%d, joints=%zu",
    serial_port_.c_str(), baud_rate_, info_.joints.size());

  size_t num_joints = info_.joints.size();
  hw_positions_.resize(num_joints, 0.0);
  hw_velocities_.resize(num_joints, 0.0);
  hw_commands_.resize(num_joints, 0.0);
  prev_positions_.resize(num_joints, 0.0);

  return hardware_interface::CallbackReturn::SUCCESS;
}

hardware_interface::CallbackReturn ServoInterface::on_configure(
  const rclcpp_lifecycle::State & /*previous_state*/)
{
  RCLCPP_INFO(rclcpp::get_logger("CompanionHeadServoInterface"),
    "Configuring: Opening serial port %s", serial_port_.c_str());

  serial_ = std::make_unique<SerialPort>();
  if (!serial_->open(serial_port_, baud_rate_)) {
    RCLCPP_ERROR(rclcpp::get_logger("CompanionHeadServoInterface"),
      "Failed to open serial port %s", serial_port_.c_str());
    return hardware_interface::CallbackReturn::ERROR;
  }

  RCLCPP_INFO(rclcpp::get_logger("CompanionHeadServoInterface"),
    "Serial port opened successfully");

  return hardware_interface::CallbackReturn::SUCCESS;
}

hardware_interface::CallbackReturn ServoInterface::on_cleanup(
  const rclcpp_lifecycle::State & /*previous_state*/)
{
  if (serial_) {
    serial_->close();
    serial_.reset();
  }
  return hardware_interface::CallbackReturn::SUCCESS;
}

hardware_interface::CallbackReturn ServoInterface::on_activate(
  const rclcpp_lifecycle::State & /*previous_state*/)
{
  RCLCPP_INFO(rclcpp::get_logger("CompanionHeadServoInterface"),
    "Activating Companion Head Servo Interface");

  for (size_t i = 0; i < hw_commands_.size(); ++i) {
    hw_commands_[i] = hw_positions_[i];
  }

  return hardware_interface::CallbackReturn::SUCCESS;
}

hardware_interface::CallbackReturn ServoInterface::on_deactivate(
  const rclcpp_lifecycle::State & /*previous_state*/)
{
  RCLCPP_INFO(rclcpp::get_logger("CompanionHeadServoInterface"),
    "Deactivating Companion Head Servo Interface");
  return hardware_interface::CallbackReturn::SUCCESS;
}

std::vector<hardware_interface::StateInterface>
ServoInterface::export_state_interfaces()
{
  std::vector<hardware_interface::StateInterface> state_interfaces;

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
ServoInterface::export_command_interfaces()
{
  std::vector<hardware_interface::CommandInterface> command_interfaces;

  for (size_t i = 0; i < info_.joints.size(); ++i) {
    command_interfaces.emplace_back(
      hardware_interface::CommandInterface(
        info_.joints[i].name, hardware_interface::HW_IF_POSITION, &hw_commands_[i]));
  }

  return command_interfaces;
}

hardware_interface::return_type ServoInterface::read(
  const rclcpp::Time & /*time*/, const rclcpp::Duration & period)
{
  if (!serial_ || !serial_->is_open()) {
    return hardware_interface::return_type::ERROR;
  }

  std::string line = serial_->read_line();
  while (!line.empty()) {
    parse_feedback(line);
    line = serial_->read_line();
  }

  double dt = period.seconds();
  if (dt > 0.0) {
    for (size_t i = 0; i < hw_positions_.size(); ++i) {
      hw_velocities_[i] = (hw_positions_[i] - prev_positions_[i]) / dt;
      prev_positions_[i] = hw_positions_[i];
    }
  }

  return hardware_interface::return_type::OK;
}

hardware_interface::return_type ServoInterface::write(
  const rclcpp::Time & /*time*/, const rclcpp::Duration & /*period*/)
{
  if (!serial_ || !serial_->is_open()) {
    return hardware_interface::return_type::ERROR;
  }

  send_commands();
  return hardware_interface::return_type::OK;
}

void ServoInterface::parse_feedback(const std::string & msg)
{
  // Expected: SERVO_POS <pan_deg> <tilt_deg> or SERVO_POS,<pan_deg>,<tilt_deg>
  if (msg.find("SERVO_POS") != 0) {
    return;
  }

  std::string data = msg.substr(9);
  std::replace(data.begin(), data.end(), ',', ' ');
  std::istringstream iss(data);
  double pan_deg = 90.0;
  double tilt_deg = 90.0;

  if (iss >> pan_deg >> tilt_deg) {
    if (hw_positions_.size() >= 2) {
      // 90 deg = 0 rad
      hw_positions_[0] = deg_to_rad(pan_deg - 90.0);
      hw_positions_[1] = deg_to_rad(tilt_deg - 90.0);
    }
  }
}

void ServoInterface::send_commands()
{
  if (hw_commands_.size() < 2) {
    return;
  }

  double pan_deg = rad_to_deg(hw_commands_[0]) + 90.0;
  double tilt_deg = rad_to_deg(hw_commands_[1]) + 90.0;

  // Clamp 0-180
  pan_deg = std::max(0.0, std::min(180.0, pan_deg));
  tilt_deg = std::max(0.0, std::min(180.0, tilt_deg));

  std::ostringstream ss;
  ss << "SERVO " << static_cast<int>(std::round(pan_deg)) << " "
     << static_cast<int>(std::round(tilt_deg)) << "\n";

  serial_->write(ss.str());
}

double ServoInterface::rad_to_deg(double rad) const
{
  return rad * 180.0 / M_PI;
}

double ServoInterface::deg_to_rad(double deg) const
{
  return deg * M_PI / 180.0;
}

}  // namespace companion_head_hardware

#include "pluginlib/class_list_macros.hpp"
PLUGINLIB_EXPORT_CLASS(
  companion_head_hardware::ServoInterface,
  hardware_interface::SystemInterface)
