#include <array>
#include <algorithm>
#include <cmath>
#include <chrono>
#include <memory>
#include <string>
#include <vector>
#include <mutex>
#include <thread>

#include <gazebo/common/Events.hh>
#include <gazebo/common/Plugin.hh>
#include <gazebo/physics/physics.hh>
#include <ignition/math/Pose3.hh>
#include <ignition/math/Quaternion.hh>
#include <ignition/math/Vector3.hh>

#include "geometry_msgs/msg/transform_stamped.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "rclcpp/rclcpp.hpp"
#include "tf2_ros/transform_broadcaster.h"

namespace gazebo
{
namespace
{
constexpr double kPi = 3.14159265358979323846;
constexpr double kFemurNeutral = 0.80;
constexpr double kTibiaNeutral = -1.25;

struct Leg
{
  std::string name;
  double hip_neutral;
  double phase;
};
}  // namespace

class SpiderGazeboGaitPlugin : public ModelPlugin
{
public:
  void Load(physics::ModelPtr model, sdf::ElementPtr sdf) override
  {
    model_ = model;

    if (!rclcpp::ok()) {
      int argc = 0;
      char ** argv = nullptr;
      rclcpp::init(argc, argv);
      owns_rclcpp_ = true;
    }

    ros_node_ = rclcpp::Node::make_shared("spider_gazebo_gait_plugin");

    cmd_vel_sub_ = ros_node_->create_subscription<geometry_msgs::msg::Twist>(
      "cmd_vel", 10,
      [this](const geometry_msgs::msg::Twist::SharedPtr msg) {
        std::lock_guard<std::mutex> lock(cmd_mutex_);
        last_cmd_vel_ = *msg;
        last_cmd_time_ = std::chrono::steady_clock::now();
      });
    odom_pub_ = ros_node_->create_publisher<nav_msgs::msg::Odometry>("odom", 10);
    tf_broadcaster_ = std::make_shared<tf2_ros::TransformBroadcaster>(ros_node_);

    executor_ = std::make_shared<rclcpp::executors::SingleThreadedExecutor>();
    executor_->add_node(ros_node_);
    spin_thread_ = std::thread([this]() { executor_->spin(); });

    if (sdf->HasElement("speed_hz")) {speed_hz_ = sdf->Get<double>("speed_hz");}
    if (sdf->HasElement("hip_swing")) {hip_swing_ = sdf->Get<double>("hip_swing");}
    if (sdf->HasElement("femur_lift")) {femur_lift_ = sdf->Get<double>("femur_lift");}
    if (sdf->HasElement("tibia_lift")) {tibia_lift_ = sdf->Get<double>("tibia_lift");}
    if (sdf->HasElement("motion_timeout")) {motion_timeout_ = sdf->Get<double>("motion_timeout");}
    if (sdf->HasElement("linear_scale")) {linear_scale_ = sdf->Get<double>("linear_scale");}
    if (sdf->HasElement("angular_scale")) {angular_scale_ = sdf->Get<double>("angular_scale");}

    for (const auto & leg : legs_) {
      JointGroup group;
      group.leg = leg;
      group.hip = model_->GetJoint(leg.name + "_hip_yaw_joint");
      group.femur = model_->GetJoint(leg.name + "_femur_pitch_joint");
      group.tibia = model_->GetJoint(leg.name + "_tibia_pitch_joint");
      if (!group.hip || !group.femur || !group.tibia) {
        gzerr << "SpiderGazeboGaitPlugin missing joints for: " << leg.name << std::endl;
        continue;
      }
      joints_.push_back(group);
    }

    model_->SetGravityMode(false);
    model_->SetWorldTwist(ignition::math::Vector3d::Zero, ignition::math::Vector3d::Zero);
    applyLegPose(false, 0.0, 0.0);

    auto pose = model_->WorldPose();
    pose.Pos().Z() = 0.04;
    pose.Rot() = ignition::math::Quaterniond(0, 0, pose.Rot().Yaw());
    model_->SetWorldPose(pose);
    last_update_time_ = model_->GetWorld()->SimTime();
    last_odom_publish_ = last_update_time_;

    gzmsg << "SpiderGazeboGaitPlugin ready (" << joints_.size()
          << " legs). Publishing /odom TF + /joint_states." << std::endl;

    update_connection_ = event::Events::ConnectWorldUpdateBegin(
      std::bind(&SpiderGazeboGaitPlugin::OnUpdate, this));
  }

  ~SpiderGazeboGaitPlugin() override
  {
    if (executor_) {executor_->cancel();}
    if (spin_thread_.joinable()) {spin_thread_.join();}
    if (owns_rclcpp_ && rclcpp::ok()) {rclcpp::shutdown();}
  }

private:
  struct JointGroup
  {
    Leg leg;
    physics::JointPtr hip;
    physics::JointPtr femur;
    physics::JointPtr tibia;
  };

  void setJointPosition(const physics::JointPtr & joint, double position)
  {
    joint->SetPosition(0, position, true);
  }

  void applyLegPose(bool walking, double t, double command_scale)
  {
    const double omega = 2.0 * kPi * speed_hz_;
    for (const auto & group : joints_) {
      if (!walking) {
        setJointPosition(group.hip, group.leg.hip_neutral);
        setJointPosition(group.femur, kFemurNeutral);
        setJointPosition(group.tibia, kTibiaNeutral);
        continue;
      }
      const double step = std::sin(omega * t + group.leg.phase);
      const double lift = std::max(0.0, std::sin(omega * t + group.leg.phase));
      setJointPosition(group.hip, group.leg.hip_neutral + hip_swing_ * command_scale * step);
      setJointPosition(group.femur, kFemurNeutral + femur_lift_ * command_scale * lift);
      setJointPosition(group.tibia, kTibiaNeutral - tibia_lift_ * command_scale * lift);
    }
  }

  void publishOdomAndJoints(const ignition::math::Pose3d & pose, double vx, double vy, double wz)
  {
    const auto sim = model_->GetWorld()->SimTime();
    if ((sim - last_odom_publish_).Double() < 0.02) {
      return;
    }
    last_odom_publish_ = sim;

    builtin_interfaces::msg::Time stamp;
    stamp.sec = static_cast<int32_t>(sim.sec);
    stamp.nanosec = static_cast<uint32_t>(sim.nsec);

    geometry_msgs::msg::TransformStamped tf;
    tf.header.stamp = stamp;
    tf.header.frame_id = "odom";
    tf.child_frame_id = "base_footprint";
    tf.transform.translation.x = pose.Pos().X();
    tf.transform.translation.y = pose.Pos().Y();
    tf.transform.translation.z = pose.Pos().Z();
    tf.transform.rotation.x = pose.Rot().X();
    tf.transform.rotation.y = pose.Rot().Y();
    tf.transform.rotation.z = pose.Rot().Z();
    tf.transform.rotation.w = pose.Rot().W();
    tf_broadcaster_->sendTransform(tf);

    nav_msgs::msg::Odometry odom;
    odom.header.stamp = stamp;
    odom.header.frame_id = "odom";
    odom.child_frame_id = "base_footprint";
    odom.pose.pose.position.x = pose.Pos().X();
    odom.pose.pose.position.y = pose.Pos().Y();
    odom.pose.pose.position.z = pose.Pos().Z();
    odom.pose.pose.orientation = tf.transform.rotation;
    odom.twist.twist.linear.x = vx;
    odom.twist.twist.linear.y = vy;
    odom.twist.twist.angular.z = wz;
    odom_pub_->publish(odom);
  }

  void OnUpdate()
  {
    const common::Time now = model_->GetWorld()->SimTime();
    double dt = (now - last_update_time_).Double();
    if (dt <= 0.0 || dt > 0.05) {dt = 0.001;}
    last_update_time_ = now;

    geometry_msgs::msg::Twist cmd_vel;
    bool cmd_active = false;
    {
      std::lock_guard<std::mutex> lock(cmd_mutex_);
      cmd_vel = last_cmd_vel_;
      const auto cmd_age = std::chrono::duration<double>(
        std::chrono::steady_clock::now() - last_cmd_time_).count();
      cmd_active = cmd_age <= motion_timeout_ &&
        (std::abs(cmd_vel.linear.x) > 0.001 ||
         std::abs(cmd_vel.linear.y) > 0.001 ||
         std::abs(cmd_vel.angular.z) > 0.001);
    }

    const double command_scale = cmd_active ?
      std::clamp(std::hypot(cmd_vel.linear.x, cmd_vel.angular.z), 0.0, 1.0) : 0.0;
    applyLegPose(cmd_active, now.Double(), command_scale);

    auto pose = model_->WorldPose();
    double vx = 0.0, vy = 0.0, wz = 0.0;
    if (cmd_active) {
      const double yaw = pose.Rot().Yaw();
      vx = cmd_vel.linear.x * linear_scale_;
      vy = cmd_vel.linear.y * linear_scale_;
      wz = cmd_vel.angular.z * angular_scale_;
      pose.Pos().X() += (vx * std::cos(yaw) - vy * std::sin(yaw)) * dt;
      pose.Pos().Y() += (vx * std::sin(yaw) + vy * std::cos(yaw)) * dt;
      pose.Rot() = ignition::math::Quaterniond(0.0, 0.0, yaw + wz * dt);
    }
    pose.Pos().Z() = 0.04;
    model_->SetWorldPose(pose);
    model_->SetWorldTwist(ignition::math::Vector3d::Zero, ignition::math::Vector3d::Zero);
    publishOdomAndJoints(pose, vx, vy, wz);
  }

  const std::array<Leg, 8> legs_{{
    {"lf", 0.0, 0.0}, {"rf", 0.0, kPi}, {"lfm", 0.0, kPi}, {"rfm", 0.0, 0.0},
    {"lrm", 0.0, 0.0}, {"rrm", 0.0, kPi}, {"lr", 0.0, kPi}, {"rr", 0.0, 0.0},
  }};

  physics::ModelPtr model_;
  event::ConnectionPtr update_connection_;
  common::Time last_update_time_;
  common::Time last_odom_publish_;
  rclcpp::Node::SharedPtr ros_node_;
  rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_sub_;
  rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr odom_pub_;
  std::shared_ptr<tf2_ros::TransformBroadcaster> tf_broadcaster_;
  std::shared_ptr<rclcpp::executors::SingleThreadedExecutor> executor_;
  std::thread spin_thread_;
  std::mutex cmd_mutex_;
  geometry_msgs::msg::Twist last_cmd_vel_;
  std::chrono::steady_clock::time_point last_cmd_time_{std::chrono::steady_clock::now()};
  std::vector<JointGroup> joints_;
  bool owns_rclcpp_{false};
  double speed_hz_{0.9};
  double hip_swing_{0.30};
  double femur_lift_{0.25};
  double tibia_lift_{0.28};
  double motion_timeout_{0.6};
  double linear_scale_{0.50};
  double angular_scale_{1.2};
};

GZ_REGISTER_MODEL_PLUGIN(SpiderGazeboGaitPlugin)
}  // namespace gazebo
