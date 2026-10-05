/**
 * @file hydrodynamics_plugin.hpp
 * @brief Gazebo plugin for underwater hydrodynamic drag simulation
 *
 * HYDRODYNAMIC DRAG PHYSICS:
 * ==========================
 * When a body moves through water, it experiences resistance forces.
 *
 * Linear (Viscous) Drag:
 * ----------------------
 * At low velocities, drag is proportional to velocity:
 *   F_drag = -D_linear * v
 *
 * Quadratic (Pressure) Drag:
 * --------------------------
 * At higher velocities, drag is proportional to velocity squared:
 *   F_drag = -D_quadratic * |v| * v
 *
 * Combined Drag Model:
 *   F_drag = -D_linear * v - D_quadratic * |v| * v
 *
 * ADDED MASS:
 * ===========
 * When accelerating in water, the body must also accelerate
 * surrounding fluid. This appears as additional inertia:
 *
 *   F = -(m + m_added) * a
 *
 * For a sphere: m_added = (2/3) * rho * V
 * For complex shapes: use added mass matrix [6x6]
 *
 * DAMPING COEFFICIENTS:
 * =====================
 * Drag differs in each direction due to geometry:
 *
 *   Surge (X): Low drag (streamlined nose)
 *   Sway (Y):  High drag (broad side)
 *   Heave (Z): High drag (top/bottom surface)
 *
 * Angular damping affects rotational motion:
 *   Roll (P):  Low damping (small moment arm)
 *   Pitch (Q): Medium damping
 *   Yaw (R):   High damping (turning resistance)
 *
 * This plugin applies both linear and angular damping forces.
 */

#ifndef REEF_DRONE_GAZEBO__HYDRODYNAMICS_PLUGIN_HPP_
#define REEF_DRONE_GAZEBO__HYDRODYNAMICS_PLUGIN_HPP_

#include <gazebo/gazebo.hh>
#include <gazebo/physics/physics.hh>
#include <gazebo/common/common.hh>
#include <rclcpp/rclcpp.hpp>

namespace reef_drone_gazebo
{

class HydrodynamicsPlugin : public gazebo::ModelPlugin
{
public:
  HydrodynamicsPlugin();
  virtual ~HydrodynamicsPlugin();

  void Load(gazebo::physics::ModelPtr model, sdf::ElementPtr sdf) override;

private:
  void OnUpdate();

  // Gazebo pointers
  gazebo::physics::ModelPtr model_;
  gazebo::physics::LinkPtr link_;
  gazebo::event::ConnectionPtr update_connection_;

  // Linear drag coefficients (N·s/m)
  ignition::math::Vector3d linear_drag_;

  // Quadratic drag coefficients (N·s²/m²)
  ignition::math::Vector3d quadratic_drag_;

  // Angular drag coefficients (N·m·s/rad)
  ignition::math::Vector3d angular_drag_;

  // ROS2 node
  rclcpp::Node::SharedPtr ros_node_;
};

}  // namespace reef_drone_gazebo

#endif  // REEF_DRONE_GAZEBO__HYDRODYNAMICS_PLUGIN_HPP_
