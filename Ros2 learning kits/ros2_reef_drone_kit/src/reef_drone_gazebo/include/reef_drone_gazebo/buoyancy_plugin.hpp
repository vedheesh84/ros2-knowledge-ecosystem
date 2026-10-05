/**
 * @file buoyancy_plugin.hpp
 * @brief Gazebo plugin for underwater buoyancy simulation
 *
 * BUOYANCY PHYSICS (Archimedes' Principle):
 * =========================================
 * When a body is submerged in a fluid, it experiences an upward force
 * equal to the weight of fluid displaced.
 *
 *   F_buoyancy = rho * g * V
 *
 * Where:
 *   rho = Fluid density (kg/m³)
 *         - Freshwater: 1000 kg/m³
 *         - Seawater: 1025 kg/m³
 *   g   = Gravitational acceleration (9.81 m/s²)
 *   V   = Displaced volume (m³)
 *
 * NEUTRAL BUOYANCY:
 * ================
 * When buoyancy force equals weight:
 *   rho_fluid * V = m_body
 *   rho_fluid * V = rho_body * V
 *   rho_fluid = rho_body
 *
 * For a typical AUV:
 *   - Slightly positive buoyancy (floats up when powered off)
 *   - Vertical thrusters counter the excess buoyancy
 *
 * CENTER OF BUOYANCY (CB):
 * =======================
 * Buoyancy force acts at the centroid of displaced volume (CB).
 * If CB is above Center of Mass (CM), the vehicle is passively stable:
 *   - Tilting creates a restoring moment
 *   - Like a pendulum hanging from CB
 *
 * This plugin applies buoyancy force at the configured center of volume.
 */

#ifndef REEF_DRONE_GAZEBO__BUOYANCY_PLUGIN_HPP_
#define REEF_DRONE_GAZEBO__BUOYANCY_PLUGIN_HPP_

#include <gazebo/gazebo.hh>
#include <gazebo/physics/physics.hh>
#include <gazebo/common/common.hh>
#include <rclcpp/rclcpp.hpp>

namespace reef_drone_gazebo
{

class BuoyancyPlugin : public gazebo::ModelPlugin
{
public:
  BuoyancyPlugin();
  virtual ~BuoyancyPlugin();

  void Load(gazebo::physics::ModelPtr model, sdf::ElementPtr sdf) override;

private:
  void OnUpdate();

  // Gazebo pointers
  gazebo::physics::ModelPtr model_;
  gazebo::physics::LinkPtr link_;
  gazebo::event::ConnectionPtr update_connection_;

  // Physical parameters
  double fluid_density_;      // kg/m³
  double displaced_volume_;   // m³
  ignition::math::Vector3d center_of_volume_;  // Relative to link origin

  // ROS2 node (for potential diagnostics)
  rclcpp::Node::SharedPtr ros_node_;
};

}  // namespace reef_drone_gazebo

#endif  // REEF_DRONE_GAZEBO__BUOYANCY_PLUGIN_HPP_
