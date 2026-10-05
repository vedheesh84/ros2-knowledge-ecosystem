#include <array>
#include <algorithm>
#include <chrono>
#include <cmath>
#include <string>

#include "geometry_msgs/msg/twist.hpp"
#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/joint_state.hpp"

using namespace std::chrono_literals;

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

class SpiderGaitNode : public rclcpp::Node
{
public:
  SpiderGaitNode()
  : Node("spider_gait_node"), start_time_(this->now())
  {
    speed_hz_ = declare_parameter<double>("speed_hz", 0.9);
    hip_swing_ = declare_parameter<double>("hip_swing", 0.28);
    femur_lift_ = declare_parameter<double>("femur_lift", 0.35);
    tibia_lift_ = declare_parameter<double>("tibia_lift", 0.40);
    motion_timeout_ = declare_parameter<double>("motion_timeout", 0.5);

    joint_pub_ = create_publisher<sensor_msgs::msg::JointState>("joint_states", 10);
    last_cmd_time_ = this->now();
    cmd_vel_sub_ = create_subscription<geometry_msgs::msg::Twist>(
      "cmd_vel", 10,
      [this](const geometry_msgs::msg::Twist::SharedPtr msg) {
        last_cmd_vel_ = *msg;
        last_cmd_time_ = this->now();
      });
    // Use node clock so use_sim_time works with Gazebo/RViz
    timer_ = rclcpp::create_timer(
      this, this->get_clock(), 20ms,
      std::bind(&SpiderGaitNode::publishGait, this));
  }

private:
  void publishGait()
  {
    const rclcpp::Time now = this->now();
    const double cmd_age = (now - last_cmd_time_).seconds();
    const bool cmd_active = cmd_age <= motion_timeout_ &&
      (std::abs(last_cmd_vel_.linear.x) > 0.001 ||
       std::abs(last_cmd_vel_.linear.y) > 0.001 ||
       std::abs(last_cmd_vel_.angular.z) > 0.001);

    sensor_msgs::msg::JointState msg;
    msg.header.stamp = now;
    msg.name.reserve(legs_.size() * 3);
    msg.position.reserve(legs_.size() * 3);

    if (!cmd_active) {
      for (const auto & leg : legs_) {
        msg.name.push_back(leg.name + "_hip_yaw_joint");
        msg.position.push_back(leg.hip_neutral);
        msg.name.push_back(leg.name + "_femur_pitch_joint");
        msg.position.push_back(kFemurNeutral);
        msg.name.push_back(leg.name + "_tibia_pitch_joint");
        msg.position.push_back(kTibiaNeutral);
      }
      joint_pub_->publish(msg);
      return;
    }

    const double t = (now - start_time_).seconds();
    const double omega = 2.0 * kPi * speed_hz_;
    const double command_scale = std::clamp(
      std::hypot(last_cmd_vel_.linear.x, last_cmd_vel_.angular.z), 0.0, 1.0);

    for (const auto & leg : legs_) {
      const double step = std::sin(omega * t + leg.phase);
      const double lift = std::max(0.0, std::sin(omega * t + leg.phase));

      msg.name.push_back(leg.name + "_hip_yaw_joint");
      msg.position.push_back(leg.hip_neutral + hip_swing_ * command_scale * step);
      msg.name.push_back(leg.name + "_femur_pitch_joint");
      msg.position.push_back(kFemurNeutral + femur_lift_ * command_scale * lift);
      msg.name.push_back(leg.name + "_tibia_pitch_joint");
      msg.position.push_back(kTibiaNeutral - tibia_lift_ * command_scale * lift);
    }

    joint_pub_->publish(msg);
  }

  // Alternating gait: front/mid/rear pairs out of phase for walking
  const std::array<Leg, 8> legs_{{
    {"lf", 0.0, 0.0},
    {"rf", 0.0, kPi},
    {"lfm", 0.0, kPi},
    {"rfm", 0.0, 0.0},
    {"lrm", 0.0, 0.0},
    {"rrm", 0.0, kPi},
    {"lr", 0.0, kPi},
    {"rr", 0.0, 0.0},
  }};

  rclcpp::Time start_time_;
  rclcpp::Publisher<sensor_msgs::msg::JointState>::SharedPtr joint_pub_;
  rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_sub_;
  rclcpp::TimerBase::SharedPtr timer_;
  double speed_hz_;
  double hip_swing_;
  double femur_lift_;
  double tibia_lift_;
  double motion_timeout_;
  geometry_msgs::msg::Twist last_cmd_vel_;
  rclcpp::Time last_cmd_time_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<SpiderGaitNode>());
  rclcpp::shutdown();
  return 0;
}
