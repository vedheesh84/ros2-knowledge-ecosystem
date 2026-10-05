/**
 * @file imu_hardware.cpp
 * @brief Implementation of IMU hardware interface for quadruped robot
 *
 * LEARNING POINTS:
 *
 * 1. IMU DATA
 *    - Orientation: quaternion (x, y, z, w) representing body attitude
 *    - Angular velocity: body rotation rates (rad/s)
 *    - Linear acceleration: includes gravity when stationary
 *
 * 2. STATE ESTIMATION
 *    IMU is fused with:
 *    - Leg kinematics (for velocity)
 *    - Contact detection (for drift correction)
 *
 * 3. COORDINATE FRAMES
 *    IMU outputs are in imu_link frame.
 *    State estimator transforms to world frame.
 */

#include "quadruped_hardware/imu_hardware.hpp"

namespace quadruped_hardware
{

hardware_interface::CallbackReturn IMUHardwareInterface::on_init(
  const hardware_interface::HardwareInfo & info)
{
  if (hardware_interface::SensorInterface::on_init(info) !=
    hardware_interface::CallbackReturn::SUCCESS)
  {
    return hardware_interface::CallbackReturn::ERROR;
  }

  // Parse parameters
  if (info_.hardware_parameters.count("frame_id")) {
    frame_id_ = info_.hardware_parameters.at("frame_id");
  } else {
    frame_id_ = "imu_link";
  }

  // Verify sensor configuration
  if (info_.sensors.size() != 1) {
    RCLCPP_ERROR(logger_, "Expected exactly one sensor, got %zu", info_.sensors.size());
    return hardware_interface::CallbackReturn::ERROR;
  }

  const auto & sensor = info_.sensors[0];
  if (sensor.state_interfaces.size() != 10) {
    RCLCPP_ERROR(logger_,
      "IMU sensor must have 10 state interfaces (4 orientation + 3 angular_velocity + 3 linear_acceleration)");
    return hardware_interface::CallbackReturn::ERROR;
  }

  RCLCPP_INFO(logger_, "Initialized IMUHardwareInterface (frame: %s)", frame_id_.c_str());
  return hardware_interface::CallbackReturn::SUCCESS;
}

hardware_interface::CallbackReturn IMUHardwareInterface::on_configure(
  const rclcpp_lifecycle::State & /*previous_state*/)
{
  RCLCPP_INFO(logger_, "Configuring IMUHardwareInterface...");

  // Initialize to identity orientation with gravity
  orientation_x_ = 0.0;
  orientation_y_ = 0.0;
  orientation_z_ = 0.0;
  orientation_w_ = 1.0;

  angular_velocity_x_ = 0.0;
  angular_velocity_y_ = 0.0;
  angular_velocity_z_ = 0.0;

  linear_acceleration_x_ = 0.0;
  linear_acceleration_y_ = 0.0;
  linear_acceleration_z_ = 9.81;  // Gravity in Z (robot upright)

  return hardware_interface::CallbackReturn::SUCCESS;
}

hardware_interface::CallbackReturn IMUHardwareInterface::on_activate(
  const rclcpp_lifecycle::State & /*previous_state*/)
{
  RCLCPP_INFO(logger_, "Activating IMUHardwareInterface...");
  return hardware_interface::CallbackReturn::SUCCESS;
}

hardware_interface::CallbackReturn IMUHardwareInterface::on_deactivate(
  const rclcpp_lifecycle::State & /*previous_state*/)
{
  RCLCPP_INFO(logger_, "Deactivating IMUHardwareInterface...");
  return hardware_interface::CallbackReturn::SUCCESS;
}

hardware_interface::CallbackReturn IMUHardwareInterface::on_cleanup(
  const rclcpp_lifecycle::State & /*previous_state*/)
{
  RCLCPP_INFO(logger_, "Cleaning up IMUHardwareInterface...");
  return hardware_interface::CallbackReturn::SUCCESS;
}

std::vector<hardware_interface::StateInterface>
IMUHardwareInterface::export_state_interfaces()
{
  std::vector<hardware_interface::StateInterface> state_interfaces;

  const std::string & sensor_name = info_.sensors[0].name;

  // Orientation (quaternion)
  state_interfaces.emplace_back(sensor_name, "orientation.x", &orientation_x_);
  state_interfaces.emplace_back(sensor_name, "orientation.y", &orientation_y_);
  state_interfaces.emplace_back(sensor_name, "orientation.z", &orientation_z_);
  state_interfaces.emplace_back(sensor_name, "orientation.w", &orientation_w_);

  // Angular velocity
  state_interfaces.emplace_back(sensor_name, "angular_velocity.x", &angular_velocity_x_);
  state_interfaces.emplace_back(sensor_name, "angular_velocity.y", &angular_velocity_y_);
  state_interfaces.emplace_back(sensor_name, "angular_velocity.z", &angular_velocity_z_);

  // Linear acceleration
  state_interfaces.emplace_back(sensor_name, "linear_acceleration.x", &linear_acceleration_x_);
  state_interfaces.emplace_back(sensor_name, "linear_acceleration.y", &linear_acceleration_y_);
  state_interfaces.emplace_back(sensor_name, "linear_acceleration.z", &linear_acceleration_z_);

  return state_interfaces;
}

hardware_interface::return_type IMUHardwareInterface::read(
  const rclcpp::Time & /*time*/,
  const rclcpp::Duration & /*period*/)
{
  // In mock mode: return static values (robot upright, stationary)
  // In real hardware: read from IMU sensor

  // Identity orientation (no rotation)
  orientation_x_ = 0.0;
  orientation_y_ = 0.0;
  orientation_z_ = 0.0;
  orientation_w_ = 1.0;

  // Zero angular velocity
  angular_velocity_x_ = 0.0;
  angular_velocity_y_ = 0.0;
  angular_velocity_z_ = 0.0;

  // Gravity in Z axis (robot upright)
  linear_acceleration_x_ = 0.0;
  linear_acceleration_y_ = 0.0;
  linear_acceleration_z_ = 9.81;

  return hardware_interface::return_type::OK;
}

}  // namespace quadruped_hardware

#include "pluginlib/class_list_macros.hpp"
PLUGINLIB_EXPORT_CLASS(
  quadruped_hardware::IMUHardwareInterface, hardware_interface::SensorInterface)
