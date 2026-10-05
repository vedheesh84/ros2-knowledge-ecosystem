/**
 * @file leg_hardware.cpp
 * @brief Implementation of leg hardware interface for quadruped robot
 *
 * LEARNING POINTS:
 *
 * 1. EFFORT CONTROL (not position)
 *    Legged robots use effort (torque) control because:
 *    - Need compliant contact with ground
 *    - Position control is too stiff for dynamic locomotion
 *    - MPC outputs desired forces, not positions
 *
 * 2. HIGH UPDATE RATE
 *    Runs at 1000 Hz because:
 *    - Contact dynamics change rapidly
 *    - Balancing requires fast feedback
 *    - Slower rates cause instability
 *
 * 3. SIMPLE DYNAMICS MODEL
 *    In mock mode, we simulate:
 *    velocity = (effort - damping * velocity) / inertia * dt
 *    position += velocity * dt
 */

#include "quadruped_hardware/leg_hardware.hpp"

#include <algorithm>
#include <cmath>
#include <limits>

namespace quadruped_hardware
{

hardware_interface::CallbackReturn LegHardwareInterface::on_init(
  const hardware_interface::HardwareInfo & info)
{
  if (hardware_interface::SystemInterface::on_init(info) !=
    hardware_interface::CallbackReturn::SUCCESS)
  {
    return hardware_interface::CallbackReturn::ERROR;
  }

  // Parse hardware parameters from URDF
  if (info_.hardware_parameters.count("serial_port")) {
    serial_port_ = info_.hardware_parameters.at("serial_port");
  } else {
    serial_port_ = "/dev/ttyUSB0";
  }

  if (info_.hardware_parameters.count("baud_rate")) {
    baud_rate_ = std::stoi(info_.hardware_parameters.at("baud_rate"));
  } else {
    baud_rate_ = 1000000;
  }

  // Extract joint names and validate interfaces
  joint_names_.clear();
  for (const auto & joint : info_.joints) {
    joint_names_.push_back(joint.name);

    // Verify command interfaces
    if (joint.command_interfaces.size() != 1 ||
      joint.command_interfaces[0].name != "effort")
    {
      RCLCPP_ERROR(logger_,
        "Joint '%s' must have exactly one 'effort' command interface",
        joint.name.c_str());
      return hardware_interface::CallbackReturn::ERROR;
    }

    // Verify state interfaces (position, velocity, effort)
    if (joint.state_interfaces.size() != 3) {
      RCLCPP_ERROR(logger_,
        "Joint '%s' must have 3 state interfaces (position, velocity, effort)",
        joint.name.c_str());
      return hardware_interface::CallbackReturn::ERROR;
    }
  }

  // Allocate storage
  size_t num_joints = joint_names_.size();
  hw_positions_.resize(num_joints, 0.0);
  hw_velocities_.resize(num_joints, 0.0);
  hw_efforts_.resize(num_joints, 0.0);
  hw_commands_effort_.resize(num_joints, 0.0);

  RCLCPP_INFO(logger_, "Initialized LegHardwareInterface with %zu joints", num_joints);
  for (const auto & name : joint_names_) {
    RCLCPP_INFO(logger_, "  - %s", name.c_str());
  }

  return hardware_interface::CallbackReturn::SUCCESS;
}

hardware_interface::CallbackReturn LegHardwareInterface::on_configure(
  const rclcpp_lifecycle::State & /*previous_state*/)
{
  RCLCPP_INFO(logger_, "Configuring LegHardwareInterface...");

  // Reset states to default standing pose
  // HAA (hip ab/ad) = 0, HFE (hip flex) = -0.5, KFE (knee flex) = 1.0
  for (size_t i = 0; i < joint_names_.size(); ++i) {
    const std::string & name = joint_names_[i];
    if (name.find("HAA") != std::string::npos) {
      hw_positions_[i] = 0.0;
    } else if (name.find("HFE") != std::string::npos) {
      hw_positions_[i] = -0.5;
    } else if (name.find("KFE") != std::string::npos) {
      hw_positions_[i] = 1.0;
    }
    hw_velocities_[i] = 0.0;
    hw_efforts_[i] = 0.0;
    hw_commands_effort_[i] = 0.0;
  }

  // In real hardware: open serial connection here
  // For learning: we use mock mode

  RCLCPP_INFO(logger_, "Configuration complete");
  return hardware_interface::CallbackReturn::SUCCESS;
}

hardware_interface::CallbackReturn LegHardwareInterface::on_activate(
  const rclcpp_lifecycle::State & /*previous_state*/)
{
  RCLCPP_INFO(logger_, "Activating LegHardwareInterface...");

  // Zero commands on activation (safety)
  std::fill(hw_commands_effort_.begin(), hw_commands_effort_.end(), 0.0);

  return hardware_interface::CallbackReturn::SUCCESS;
}

hardware_interface::CallbackReturn LegHardwareInterface::on_deactivate(
  const rclcpp_lifecycle::State & /*previous_state*/)
{
  RCLCPP_INFO(logger_, "Deactivating LegHardwareInterface...");

  // Zero commands on deactivation (safety)
  std::fill(hw_commands_effort_.begin(), hw_commands_effort_.end(), 0.0);

  return hardware_interface::CallbackReturn::SUCCESS;
}

hardware_interface::CallbackReturn LegHardwareInterface::on_cleanup(
  const rclcpp_lifecycle::State & /*previous_state*/)
{
  RCLCPP_INFO(logger_, "Cleaning up LegHardwareInterface...");

  // In real hardware: close serial connection here

  return hardware_interface::CallbackReturn::SUCCESS;
}

std::vector<hardware_interface::StateInterface>
LegHardwareInterface::export_state_interfaces()
{
  std::vector<hardware_interface::StateInterface> state_interfaces;

  for (size_t i = 0; i < joint_names_.size(); ++i) {
    state_interfaces.emplace_back(
      joint_names_[i], "position", &hw_positions_[i]);
    state_interfaces.emplace_back(
      joint_names_[i], "velocity", &hw_velocities_[i]);
    state_interfaces.emplace_back(
      joint_names_[i], "effort", &hw_efforts_[i]);
  }

  return state_interfaces;
}

std::vector<hardware_interface::CommandInterface>
LegHardwareInterface::export_command_interfaces()
{
  std::vector<hardware_interface::CommandInterface> command_interfaces;

  for (size_t i = 0; i < joint_names_.size(); ++i) {
    command_interfaces.emplace_back(
      joint_names_[i], "effort", &hw_commands_effort_[i]);
  }

  return command_interfaces;
}

hardware_interface::return_type LegHardwareInterface::read(
  const rclcpp::Time & /*time*/,
  const rclcpp::Duration & period)
{
  // In mock mode: simulate simple dynamics
  // In real hardware: read from encoders via serial

  double dt = period.seconds();

  // Simulated dynamics parameters
  constexpr double inertia = 0.1;   // kg*m^2 (joint inertia)
  constexpr double damping = 0.5;   // Nm/(rad/s) (viscous friction)

  for (size_t i = 0; i < joint_names_.size(); ++i) {
    // Simple dynamics: τ = I * α + b * ω
    // α = (τ - b * ω) / I
    double acceleration = (hw_commands_effort_[i] - damping * hw_velocities_[i]) / inertia;

    // Integrate
    hw_velocities_[i] += acceleration * dt;
    hw_positions_[i] += hw_velocities_[i] * dt;

    // Update effort feedback (matches command in mock mode)
    hw_efforts_[i] = hw_commands_effort_[i];
  }

  return hardware_interface::return_type::OK;
}

hardware_interface::return_type LegHardwareInterface::write(
  const rclcpp::Time & /*time*/,
  const rclcpp::Duration & /*period*/)
{
  // Apply safety limits
  for (size_t i = 0; i < joint_names_.size(); ++i) {
    hw_commands_effort_[i] = std::clamp(
      hw_commands_effort_[i], -MAX_EFFORT, MAX_EFFORT);
  }

  // In real hardware: send commands via serial
  // For learning: commands are already applied in read() mock dynamics

  return hardware_interface::return_type::OK;
}

}  // namespace quadruped_hardware

#include "pluginlib/class_list_macros.hpp"
PLUGINLIB_EXPORT_CLASS(
  quadruped_hardware::LegHardwareInterface, hardware_interface::SystemInterface)
