/**
 * @file thruster_plugin.cpp
 * @brief Implementation of thruster force for underwater simulation
 *
 * USAGE IN SDF:
 * <plugin name="thrusters" filename="libthruster_plugin.so">
 *   <max_thrust>50</max_thrust>
 *   <time_constant>0.1</time_constant>
 *   <thruster_link>thruster_1_link</thruster_link>
 *   <thruster_link>thruster_2_link</thruster_link>
 *   <thruster_link>thruster_3_link</thruster_link>
 *   <thruster_link>thruster_4_link</thruster_link>
 *   <thruster_link>thruster_5_link</thruster_link>
 *   <thruster_link>thruster_6_link</thruster_link>
 * </plugin>
 *
 * ROS2 TOPICS:
 *   Subscribe: /thrusters/cmd (Float64MultiArray)
 *     - 6 values, one per thruster
 *     - Range: -1.0 to +1.0
 */

#include "reef_drone_gazebo/thruster_plugin.hpp"
#include <gazebo_ros/node.hpp>

namespace reef_drone_gazebo
{

ThrusterPlugin::ThrusterPlugin()
: max_thrust_(50.0),
  time_constant_(0.1)
{
}

ThrusterPlugin::~ThrusterPlugin()
{
}

void ThrusterPlugin::Load(gazebo::physics::ModelPtr model, sdf::ElementPtr sdf)
{
  model_ = model;

  // Get ROS node
  ros_node_ = gazebo_ros::Node::Get(sdf);

  // Get parameters
  if (sdf->HasElement("max_thrust"))
  {
    max_thrust_ = sdf->Get<double>("max_thrust");
  }

  if (sdf->HasElement("time_constant"))
  {
    time_constant_ = sdf->Get<double>("time_constant");
  }

  // Get thruster links
  sdf::ElementPtr thruster_elem = sdf->GetElement("thruster_link");
  while (thruster_elem)
  {
    std::string link_name = thruster_elem->Get<std::string>();
    gazebo::physics::LinkPtr link = model_->GetLink(link_name);

    if (link)
    {
      thruster_links_.push_back(link);
      commands_.push_back(0.0);
      thrusts_.push_back(0.0);
      RCLCPP_INFO(ros_node_->get_logger(),
        "ThrusterPlugin: Added thruster '%s'", link_name.c_str());
    }
    else
    {
      RCLCPP_WARN(ros_node_->get_logger(),
        "ThrusterPlugin: Link '%s' not found!", link_name.c_str());
    }

    thruster_elem = thruster_elem->GetNextElement("thruster_link");
  }

  if (thruster_links_.empty())
  {
    RCLCPP_ERROR(ros_node_->get_logger(),
      "ThrusterPlugin: No thruster links found!");
    return;
  }

  RCLCPP_INFO(ros_node_->get_logger(),
    "ThrusterPlugin loaded: %zu thrusters, max_thrust=%.1f N, tau=%.2f s",
    thruster_links_.size(), max_thrust_, time_constant_);

  // Create subscription for thruster commands
  cmd_sub_ = ros_node_->create_subscription<std_msgs::msg::Float64MultiArray>(
    "/thrusters/cmd", 10,
    std::bind(&ThrusterPlugin::ThrusterCallback, this, std::placeholders::_1));

  // Connect to update event
  update_connection_ = gazebo::event::Events::ConnectWorldUpdateBegin(
    std::bind(&ThrusterPlugin::OnUpdate, this));
}

void ThrusterPlugin::ThrusterCallback(const std_msgs::msg::Float64MultiArray::SharedPtr msg)
{
  std::lock_guard<std::mutex> lock(cmd_mutex_);

  size_t n = std::min(msg->data.size(), thruster_links_.size());
  for (size_t i = 0; i < n; ++i)
  {
    // Clamp command to [-1, 1]
    commands_[i] = std::max(-1.0, std::min(1.0, msg->data[i]));
  }
}

void ThrusterPlugin::OnUpdate()
{
  if (thruster_links_.empty())
    return;

  // Get simulation timestep
  double dt = model_->GetWorld()->Physics()->GetMaxStepSize();

  // First-order dynamics: alpha = dt / (tau + dt)
  double alpha = dt / (time_constant_ + dt);

  std::lock_guard<std::mutex> lock(cmd_mutex_);

  for (size_t i = 0; i < thruster_links_.size(); ++i)
  {
    // Calculate commanded thrust: F = F_max * cmd * |cmd|
    // This gives quadratic relationship (like real thrusters)
    double cmd_thrust = max_thrust_ * commands_[i] * std::abs(commands_[i]);

    // Apply first-order dynamics
    thrusts_[i] = alpha * cmd_thrust + (1.0 - alpha) * thrusts_[i];

    // Apply thrust force along thruster's +X axis
    ignition::math::Vector3d force_local(thrusts_[i], 0, 0);
    thruster_links_[i]->AddRelativeForce(force_local);
  }
}

// Register plugin with Gazebo
GZ_REGISTER_MODEL_PLUGIN(ThrusterPlugin)

}  // namespace reef_drone_gazebo
