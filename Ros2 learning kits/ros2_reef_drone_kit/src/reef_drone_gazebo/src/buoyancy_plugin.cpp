/**
 * @file buoyancy_plugin.cpp
 * @brief Implementation of buoyancy force for underwater simulation
 *
 * USAGE IN SDF:
 * <plugin name="buoyancy" filename="libbuoyancy_plugin.so">
 *   <link_name>base_link</link_name>
 *   <fluid_density>1025</fluid_density>
 *   <displaced_volume>0.0114</displaced_volume>
 *   <center_of_volume>0 0 0.02</center_of_volume>
 * </plugin>
 */

#include "reef_drone_gazebo/buoyancy_plugin.hpp"
#include <gazebo_ros/node.hpp>

namespace reef_drone_gazebo
{

BuoyancyPlugin::BuoyancyPlugin()
: fluid_density_(1025.0),    // Seawater default
  displaced_volume_(0.0114)  // ~11.5 kg neutral buoyancy
{
}

BuoyancyPlugin::~BuoyancyPlugin()
{
}

void BuoyancyPlugin::Load(gazebo::physics::ModelPtr model, sdf::ElementPtr sdf)
{
  model_ = model;

  // Get ROS node from Gazebo
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
      "BuoyancyPlugin: Link '%s' not found!", link_name.c_str());
    return;
  }

  // Get fluid density (kg/m³)
  if (sdf->HasElement("fluid_density"))
  {
    fluid_density_ = sdf->Get<double>("fluid_density");
  }

  // Get displaced volume (m³)
  if (sdf->HasElement("displaced_volume"))
  {
    displaced_volume_ = sdf->Get<double>("displaced_volume");
  }

  // Get center of volume relative to link origin
  center_of_volume_ = ignition::math::Vector3d(0, 0, 0.02);
  if (sdf->HasElement("center_of_volume"))
  {
    center_of_volume_ = sdf->Get<ignition::math::Vector3d>("center_of_volume");
  }

  // Calculate buoyancy force
  double g = 9.81;
  double buoyancy_force = fluid_density_ * g * displaced_volume_;

  RCLCPP_INFO(ros_node_->get_logger(),
    "BuoyancyPlugin loaded for '%s': rho=%.1f kg/m³, V=%.4f m³, F_b=%.2f N",
    link_name.c_str(), fluid_density_, displaced_volume_, buoyancy_force);

  // Connect to Gazebo update event
  update_connection_ = gazebo::event::Events::ConnectWorldUpdateBegin(
    std::bind(&BuoyancyPlugin::OnUpdate, this));
}

void BuoyancyPlugin::OnUpdate()
{
  if (!link_)
    return;

  // Calculate buoyancy force magnitude
  // F = rho * g * V (always upward in world frame)
  double g = 9.81;
  double buoyancy_magnitude = fluid_density_ * g * displaced_volume_;

  // Buoyancy force in world frame (always +Z)
  ignition::math::Vector3d force_world(0, 0, buoyancy_magnitude);

  // Get link pose to transform center of volume to world frame
  ignition::math::Pose3d link_pose = link_->WorldPose();

  // Center of volume in world frame
  ignition::math::Vector3d cov_world = link_pose.Rot().RotateVector(center_of_volume_);

  // Apply force at center of volume
  // This creates a moment if CoV != CoM, providing passive stability
  link_->AddForceAtRelativePosition(force_world, center_of_volume_);
}

// Register plugin with Gazebo
GZ_REGISTER_MODEL_PLUGIN(BuoyancyPlugin)

}  // namespace reef_drone_gazebo
