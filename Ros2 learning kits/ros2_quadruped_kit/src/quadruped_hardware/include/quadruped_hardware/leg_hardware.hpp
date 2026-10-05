/**
 * @file leg_hardware.hpp
 * @brief ros2_control hardware interface for quadruped leg joints
 *
 * LEARNING OBJECTIVES:
 * - Understanding hardware_interface::SystemInterface
 * - Effort-based joint control for legged robots
 * - State feedback: position, velocity, effort
 *
 * This interface manages 12 joints (4 legs × 3 joints each):
 * - Command interface: effort (torque in Nm)
 * - State interfaces: position (rad), velocity (rad/s), effort (Nm)
 */

#ifndef QUADRUPED_HARDWARE__LEG_HARDWARE_HPP_
#define QUADRUPED_HARDWARE__LEG_HARDWARE_HPP_

#include <memory>
#include <string>
#include <vector>

#include "hardware_interface/system_interface.hpp"
#include "hardware_interface/handle.hpp"
#include "hardware_interface/hardware_info.hpp"
#include "hardware_interface/types/hardware_interface_return_values.hpp"
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_lifecycle/state.hpp"

namespace quadruped_hardware
{

class LegHardwareInterface : public hardware_interface::SystemInterface
{
public:
  RCLCPP_SHARED_PTR_DEFINITIONS(LegHardwareInterface)

  /**
   * @brief Initialize hardware from URDF information
   *
   * Called once during controller_manager initialization.
   * Parses URDF <ros2_control> tag for parameters.
   */
  hardware_interface::CallbackReturn on_init(
    const hardware_interface::HardwareInfo & info) override;

  /**
   * @brief Configure hardware (allocate buffers, open connections)
   */
  hardware_interface::CallbackReturn on_configure(
    const rclcpp_lifecycle::State & previous_state) override;

  /**
   * @brief Activate hardware (start control loop)
   */
  hardware_interface::CallbackReturn on_activate(
    const rclcpp_lifecycle::State & previous_state) override;

  /**
   * @brief Deactivate hardware (stop control loop)
   */
  hardware_interface::CallbackReturn on_deactivate(
    const rclcpp_lifecycle::State & previous_state) override;

  /**
   * @brief Cleanup hardware (close connections, free buffers)
   */
  hardware_interface::CallbackReturn on_cleanup(
    const rclcpp_lifecycle::State & previous_state) override;

  /**
   * @brief Export state interfaces to controller_manager
   *
   * For each joint, exports:
   * - position (rad)
   * - velocity (rad/s)
   * - effort (Nm)
   */
  std::vector<hardware_interface::StateInterface> export_state_interfaces() override;

  /**
   * @brief Export command interfaces to controller_manager
   *
   * For each joint, exports:
   * - effort (Nm) - torque commands for the joint
   */
  std::vector<hardware_interface::CommandInterface> export_command_interfaces() override;

  /**
   * @brief Read joint states from hardware
   *
   * Called at controller_manager update rate (1000 Hz for legged robots).
   * In simulation/mock mode, uses simple dynamics model.
   */
  hardware_interface::return_type read(
    const rclcpp::Time & time,
    const rclcpp::Duration & period) override;

  /**
   * @brief Write commands to hardware
   *
   * Sends effort commands to actuators.
   * Includes safety limits and watchdog.
   */
  hardware_interface::return_type write(
    const rclcpp::Time & time,
    const rclcpp::Duration & period) override;

private:
  // Hardware parameters
  std::string serial_port_;
  int baud_rate_;

  // Joint names (from URDF)
  std::vector<std::string> joint_names_;

  // State storage (12 joints)
  std::vector<double> hw_positions_;
  std::vector<double> hw_velocities_;
  std::vector<double> hw_efforts_;

  // Command storage
  std::vector<double> hw_commands_effort_;

  // Safety limits
  static constexpr double MAX_EFFORT = 30.0;  // Nm

  // Logger
  rclcpp::Logger logger_{rclcpp::get_logger("LegHardwareInterface")};
};

}  // namespace quadruped_hardware

#endif  // QUADRUPED_HARDWARE__LEG_HARDWARE_HPP_
