/**
 * @file hydrodynamics_plugin.cpp
 * @brief Implementation of hydrodynamic drag for underwater simulation
 *
 * USAGE IN SDF:
 * <plugin name="hydrodynamics" filename="libhydrodynamics_plugin.so">
 *   <link_name>base_link</link_name>
 *   <linear_drag>5 10 10</linear_drag>
 *   <quadratic_drag>20 40 40</quadratic_drag>
 *   <angular_drag>0.5 0.5 1.0</angular_drag>
 * </plugin>
 *
 * PARAMETER TUNING:
 * ================
 * Higher drag = slower response, more stable
 * Lower drag = faster response, less damped
 *
 * Typical values for small AUV:
 *   Linear: 5-20 N·s/m
 *   Quadratic: 20-100 N·s²/m²
 *   Angular: 0.5-2.0 N·m·s/rad
 */

#include "reef_drone_gazebo/hydrodynamics_plugin.hpp"
#include <gazebo_ros/node.hpp>

namespace reef_drone_gazebo
{

HydrodynamicsPlugin::HydrodynamicsPlugin()
: linear_drag_(5.0, 10.0, 10.0),
  quadratic_drag_(20.0, 40.0, 40.0),
  angular_drag_(0.5, 0.5, 1.0)
{
}

HydrodynamicsPlugin::~HydrodynamicsPlugin()
{
}

void HydrodynamicsPlugin::Load(gazebo::physics::ModelPtr model, sdf::ElementPtr sdf)
{
  model_ = model;

  // Get ROS node
  ros_node_ = gazebo_ros::Node::Get(sdf);

  // Get link name
  std::string link_name = "base_link";
  if (sdf->HasElement("link_name"))
  {
    link_name = sdf->Get<std::string>("link_name");
  }

  link_ = model_->GetLink(link_name);
  if (!link_)
  {
    RCLCPP_ERROR(ros_node_->get_logger(),
      "HydrodynamicsPlugin: Link '%s' not found!", link_name.c_str());
    return;
  }

  // Get drag coefficients
  if (sdf->HasElement("linear_drag"))
  {
    linear_drag_ = sdf->Get<ignition::math::Vector3d>("linear_drag");
  }

  if (sdf->HasElement("quadratic_drag"))
  {
    quadratic_drag_ = sdf->Get<ignition::math::Vector3d>("quadratic_drag");
  }

  if (sdf->HasElement("angular_drag"))
  {
    angular_drag_ = sdf->Get<ignition::math::Vector3d>("angular_drag");
  }

  RCLCPP_INFO(ros_node_->get_logger(),
    "HydrodynamicsPlugin loaded for '%s'", link_name.c_str());
  RCLCPP_INFO(ros_node_->get_logger(),
    "  Linear drag: [%.1f, %.1f, %.1f]",
    linear_drag_.X(), linear_drag_.Y(), linear_drag_.Z());
  RCLCPP_INFO(ros_node_->get_logger(),
    "  Quadratic drag: [%.1f, %.1f, %.1f]",
    quadratic_drag_.X(), quadratic_drag_.Y(), quadratic_drag_.Z());
  RCLCPP_INFO(ros_node_->get_logger(),
    "  Angular drag: [%.1f, %.1f, %.1f]",
    angular_drag_.X(), angular_drag_.Y(), angular_drag_.Z());

  // Connect to update event
  update_connection_ = gazebo::event::Events::ConnectWorldUpdateBegin(
    std::bind(&HydrodynamicsPlugin::OnUpdate, this));
}

void HydrodynamicsPlugin::OnUpdate()
{
  if (!link_)
    return;

  // Get velocities in body frame
  ignition::math::Vector3d linear_vel = link_->RelativeLinearVel();
  ignition::math::Vector3d angular_vel = link_->RelativeAngularVel();

  // Calculate linear drag force in body frame
  // F_drag = -D_linear * v - D_quadratic * |v| * v
  ignition::math::Vector3d linear_drag_force;
  linear_drag_force.X() = -linear_drag_.X() * linear_vel.X()
                          - quadratic_drag_.X() * std::abs(linear_vel.X()) * linear_vel.X();
  linear_drag_force.Y() = -linear_drag_.Y() * linear_vel.Y()
                          - quadratic_drag_.Y() * std::abs(linear_vel.Y()) * linear_vel.Y();
  linear_drag_force.Z() = -linear_drag_.Z() * linear_vel.Z()
                          - quadratic_drag_.Z() * std::abs(linear_vel.Z()) * linear_vel.Z();

  // Calculate angular drag torque in body frame
  // T_drag = -D_angular * omega
  ignition::math::Vector3d angular_drag_torque;
  angular_drag_torque.X() = -angular_drag_.X() * angular_vel.X();
  angular_drag_torque.Y() = -angular_drag_.Y() * angular_vel.Y();
  angular_drag_torque.Z() = -angular_drag_.Z() * angular_vel.Z();

  // Apply forces and torques (in body frame)
  link_->AddRelativeForce(linear_drag_force);
  link_->AddRelativeTorque(angular_drag_torque);
}

// Register plugin with Gazebo
GZ_REGISTER_MODEL_PLUGIN(HydrodynamicsPlugin)

}  // namespace reef_drone_gazebo
