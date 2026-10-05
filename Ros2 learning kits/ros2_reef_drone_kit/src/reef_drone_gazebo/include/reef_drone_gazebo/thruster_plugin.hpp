/**
 * @file thruster_plugin.hpp
 * @brief Gazebo plugin for underwater thruster simulation
 *
 * THRUSTER PHYSICS:
 * =================
 * Marine thrusters generate thrust by accelerating water.
 *
 * Basic Thrust Model:
 * -------------------
 * Thrust is approximately proportional to RPM squared:
 *
 *   F = Kt * |n| * n
 *
 * Where:
 *   Kt = Thrust coefficient (N/RPM²)
 *   n  = Propeller RPM
 *
 * The |n| * n term gives bidirectional thrust (+ or - based on rotation).
 *
 * Simplified Command Model:
 * -------------------------
 * For this simulation, we use normalized commands (-1 to +1):
 *
 *   F = F_max * cmd * |cmd|
 *
 * Where:
 *   F_max = Maximum thrust (N)
 *   cmd   = Normalized command (-1 to +1)
 *
 * THRUSTER DYNAMICS:
 * ==================
 * Real thrusters don't respond instantly. First-order dynamics:
 *
 *   T_actual(t) = T_cmd * (1 - e^(-t/tau))
 *
 * Where tau is the time constant (~0.05-0.2s for small thrusters).
 *
 * Discrete approximation:
 *   T_actual[k+1] = alpha * T_cmd + (1-alpha) * T_actual[k]
 *   alpha = dt / (tau + dt)
 *
 * THRUST DIRECTION:
 * =================
 * Thrust is applied along the thruster's +X axis in its local frame.
 * Positive thrust pushes fluid backward, propelling the vehicle forward.
 *
 * ROS2 INTERFACE:
 * ===============
 * Subscribes to: /thrusters/cmd (std_msgs/Float64MultiArray)
 *   - Array of 6 values for 6 thrusters
 *   - Values normalized from -1.0 to +1.0
 */

#ifndef REEF_DRONE_GAZEBO__THRUSTER_PLUGIN_HPP_
#define REEF_DRONE_GAZEBO__THRUSTER_PLUGIN_HPP_

#include <gazebo/gazebo.hh>
#include <gazebo/physics/physics.hh>
#include <gazebo/common/common.hh>
#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/float64_multi_array.hpp>
#include <mutex>

namespace reef_drone_gazebo
{

class ThrusterPlugin : public gazebo::ModelPlugin
{
public:
  ThrusterPlugin();
  virtual ~ThrusterPlugin();

  void Load(gazebo::physics::ModelPtr model, sdf::ElementPtr sdf) override;

private:
  void OnUpdate();
  void ThrusterCallback(const std_msgs::msg::Float64MultiArray::SharedPtr msg);

  // Gazebo pointers
  gazebo::physics::ModelPtr model_;
  std::vector<gazebo::physics::LinkPtr> thruster_links_;
  gazebo::event::ConnectionPtr update_connection_;

  // Thruster parameters
  double max_thrust_;           // Maximum thrust per thruster (N)
  double time_constant_;        // First-order dynamics time constant (s)
  std::vector<double> commands_;    // Current commands (-1 to +1)
  std::vector<double> thrusts_;     // Actual thrust values (with dynamics)

  // Thread safety
  std::mutex cmd_mutex_;

  // ROS2 interface
  rclcpp::Node::SharedPtr ros_node_;
  rclcpp::Subscription<std_msgs::msg::Float64MultiArray>::SharedPtr cmd_sub_;
};

}  // namespace reef_drone_gazebo

#endif  // REEF_DRONE_GAZEBO__THRUSTER_PLUGIN_HPP_
