/**
 * @file imu_hardware.hpp
 * @brief ros2_control hardware interface for quadruped IMU sensor
 *
 * LEARNING OBJECTIVES:
 * - Understanding hardware_interface::SensorInterface
 * - IMU data: orientation, angular velocity, linear acceleration
 * - Sensor integration with ros2_control
 *
 * The IMU is critical for quadruped state estimation:
 * - Body orientation for balance
 * - Angular velocity for rate feedback
 * - Linear acceleration for velocity estimation
 */

#ifndef QUADRUPED_HARDWARE__IMU_HARDWARE_HPP_
#define QUADRUPED_HARDWARE__IMU_HARDWARE_HPP_

#include <memory>
#include <string>
#include <vector>

#include "hardware_interface/sensor_interface.hpp"
#include "hardware_interface/handle.hpp"
#include "hardware_interface/hardware_info.hpp"
#include "hardware_interface/types/hardware_interface_return_values.hpp"
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_lifecycle/state.hpp"

namespace quadruped_hardware
{

class IMUHardwareInterface : public hardware_interface::SensorInterface
{
public:
  RCLCPP_SHARED_PTR_DEFINITIONS(IMUHardwareInterface)

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

  /**
   * @brief Export IMU state interfaces
   *
   * Exports 10 interfaces:
   * - orientation: x, y, z, w (quaternion)
   * - angular_velocity: x, y, z (rad/s)
   * - linear_acceleration: x, y, z (m/s^2)
   */
  std::vector<hardware_interface::StateInterface> export_state_interfaces() override;

  /**
   * @brief Read IMU data from hardware
   *
   * In simulation/mock mode, returns identity orientation with gravity.
   */
  hardware_interface::return_type read(
    const rclcpp::Time & time,
    const rclcpp::Duration & period) override;

private:
  std::string frame_id_;

  // Orientation (quaternion)
  double orientation_x_{0.0};
  double orientation_y_{0.0};
  double orientation_z_{0.0};
  double orientation_w_{1.0};

  // Angular velocity (rad/s)
  double angular_velocity_x_{0.0};
  double angular_velocity_y_{0.0};
  double angular_velocity_z_{0.0};

  // Linear acceleration (m/s^2)
  double linear_acceleration_x_{0.0};
  double linear_acceleration_y_{0.0};
  double linear_acceleration_z_{9.81};  // Gravity when stationary

  rclcpp::Logger logger_{rclcpp::get_logger("IMUHardwareInterface")};
};

}  // namespace quadruped_hardware

#endif  // QUADRUPED_HARDWARE__IMU_HARDWARE_HPP_
