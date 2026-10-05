#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <memory>
#include <string>

#include "gazebo_msgs/msg/entity_state.hpp"
#include "gazebo_msgs/srv/set_entity_state.hpp"
#include "geometry_msgs/msg/transform_stamped.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "rclcpp/rclcpp.hpp"
#include "tf2_ros/transform_broadcaster.h"

using namespace std::chrono_literals;

namespace
{
double clamp_value(double value, double limit)
{
  return std::clamp(value, -limit, limit);
}

geometry_msgs::msg::Quaternion yaw_to_quaternion(double yaw)
{
  geometry_msgs::msg::Quaternion q;
  q.x = 0.0;
  q.y = 0.0;
  q.z = std::sin(yaw * 0.5);
  q.w = std::cos(yaw * 0.5);
  return q;
}

struct PropellerSpec
{
  const char * link_name;
  double x;
  double y;
  double z;
  double spin_sign;
};
}  // namespace

class ManualDroneController : public rclcpp::Node
{
public:
  ManualDroneController()
  : Node("manual_drone_controller")
  {
    entity_name_ = declare_parameter<std::string>("entity_name", "drone");
    service_name_ = declare_parameter<std::string>("set_entity_state_service", "/set_entity_state");
    command_topic_ = declare_parameter<std::string>("command_topic", "/cmd_vel");
    update_rate_ = declare_parameter<double>("update_rate", 40.0);
    max_horizontal_speed_ = declare_parameter<double>("max_horizontal_speed", 2.0);
    max_vertical_speed_ = declare_parameter<double>("max_vertical_speed", 1.0);
    max_yaw_rate_ = declare_parameter<double>("max_yaw_rate", 1.5);
    command_timeout_ = declare_parameter<double>("command_timeout", 0.6);
    min_z_ = declare_parameter<double>("min_z", 0.20);
    idle_spin_rate_ = declare_parameter<double>("idle_spin_rate", 35.0);
    command_spin_boost_ = declare_parameter<double>("command_spin_boost", 25.0);

    x_ = declare_parameter<double>("initial_x", 0.0);
    y_ = declare_parameter<double>("initial_y", 0.0);
    z_ = declare_parameter<double>("initial_z", 0.60);
    yaw_ = declare_parameter<double>("initial_yaw", 0.0);
    propeller_angles_.fill(0.0);

    state_client_ = create_client<gazebo_msgs::srv::SetEntityState>(service_name_);
    tf_broadcaster_ = std::make_unique<tf2_ros::TransformBroadcaster>(*this);
    last_command_wall_ = std::chrono::steady_clock::now();
    last_update_wall_ = last_command_wall_;

    cmd_sub_ = create_subscription<geometry_msgs::msg::Twist>(
      command_topic_,
      rclcpp::QoS(10),
      [this](const geometry_msgs::msg::Twist::SharedPtr msg) {
        latest_command_ = *msg;
        last_command_wall_ = std::chrono::steady_clock::now();
      });

    const auto period = std::chrono::duration<double>(1.0 / std::max(update_rate_, 1.0));
    timer_ = create_wall_timer(
      std::chrono::duration_cast<std::chrono::nanoseconds>(period),
      std::bind(&ManualDroneController::update, this));

    RCLCPP_INFO(
      get_logger(),
      "Manual drone controller listening on %s and controlling Gazebo entity '%s'",
      command_topic_.c_str(),
      entity_name_.c_str());
  }

private:
  void update()
  {
    const auto wall_now = std::chrono::steady_clock::now();
    const double dt = std::chrono::duration<double>(wall_now - last_update_wall_).count();
    last_update_wall_ = wall_now;

    if (!state_client_->service_is_ready()) {
      RCLCPP_WARN_THROTTLE(
        get_logger(),
        *get_clock(),
        3000,
        "Waiting for Gazebo service %s (holding pose; RViz will not drift alone)",
        service_name_.c_str());
      publish_transform(yaw_to_quaternion(yaw_));
      return;
    }

    geometry_msgs::msg::Twist command = latest_command_;
    const double command_age = std::chrono::duration<double>(wall_now - last_command_wall_).count();
    const bool command_active = command_age <= command_timeout_;
    if (!command_active) {
      command = geometry_msgs::msg::Twist();
    }

    const double vx_body = clamp_value(command.linear.x, max_horizontal_speed_);
    const double vy_body = clamp_value(command.linear.y, max_horizontal_speed_);
    const double vz = clamp_value(command.linear.z, max_vertical_speed_);
    const double yaw_rate = clamp_value(command.angular.z, max_yaw_rate_);

    const double cos_yaw = std::cos(yaw_);
    const double sin_yaw = std::sin(yaw_);
    const double vx_world = (cos_yaw * vx_body) - (sin_yaw * vy_body);
    const double vy_world = (sin_yaw * vx_body) + (cos_yaw * vy_body);

    x_ += vx_world * dt;
    y_ += vy_world * dt;
    z_ = std::max(min_z_, z_ + (vz * dt));
    yaw_ += yaw_rate * dt;
    const auto orientation = yaw_to_quaternion(yaw_);

    publish_transform(orientation);

    // Move the root link in Gazebo (keeps joints available for propeller spin).
    send_entity_state(
      entity_name_ + "::base_link",
      "world",
      x_,
      y_,
      z_,
      orientation,
      vx_world,
      vy_world,
      vz,
      yaw_rate);

    const double spin_rate = idle_spin_rate_ + (command_active ? command_spin_boost_ : 0.0);
    const std::string base_frame = entity_name_ + "::base_link";
    for (size_t i = 0; i < kPropellers.size(); ++i) {
      const auto & prop = kPropellers[i];
      propeller_angles_[i] = std::fmod(
        propeller_angles_[i] + (prop.spin_sign * spin_rate * dt),
        2.0 * M_PI);
      send_entity_state(
        entity_name_ + "::" + prop.link_name,
        base_frame,
        prop.x,
        prop.y,
        prop.z,
        yaw_to_quaternion(propeller_angles_[i]),
        0.0,
        0.0,
        0.0,
        prop.spin_sign * spin_rate);
    }
  }

  void send_entity_state(
    const std::string & name,
    const std::string & reference_frame,
    double px,
    double py,
    double pz,
    const geometry_msgs::msg::Quaternion & orientation,
    double vx,
    double vy,
    double vz,
    double yaw_rate)
  {
    auto request = std::make_shared<gazebo_msgs::srv::SetEntityState::Request>();
    request->state.name = name;
    request->state.reference_frame = reference_frame;
    request->state.pose.position.x = px;
    request->state.pose.position.y = py;
    request->state.pose.position.z = pz;
    request->state.pose.orientation = orientation;
    request->state.twist.linear.x = vx;
    request->state.twist.linear.y = vy;
    request->state.twist.linear.z = vz;
    request->state.twist.angular.z = yaw_rate;

    state_client_->async_send_request(
      request,
      [this, name](rclcpp::Client<gazebo_msgs::srv::SetEntityState>::SharedFuture future) {
        try {
          const auto response = future.get();
          if (!response->success) {
            RCLCPP_WARN_THROTTLE(
              get_logger(),
              *get_clock(),
              3000,
              "SetEntityState failed for '%s'",
              name.c_str());
          }
        } catch (const std::exception & ex) {
          RCLCPP_WARN_THROTTLE(
            get_logger(),
            *get_clock(),
            3000,
            "SetEntityState call error: %s",
            ex.what());
        }
      });
  }

  void publish_transform(const geometry_msgs::msg::Quaternion & orientation)
  {
    geometry_msgs::msg::TransformStamped transform;
    transform.header.stamp = now();
    transform.header.frame_id = "world";
    transform.child_frame_id = "base_link";
    transform.transform.translation.x = x_;
    transform.transform.translation.y = y_;
    transform.transform.translation.z = z_;
    transform.transform.rotation = orientation;
    tf_broadcaster_->sendTransform(transform);
  }

  static constexpr std::array<PropellerSpec, 4> kPropellers{{
    {"front_left_propeller", 0.32, 0.32, 0.105, 1.0},
    {"front_right_propeller", 0.32, -0.32, 0.105, -1.0},
    {"rear_left_propeller", -0.32, 0.32, 0.105, -1.0},
    {"rear_right_propeller", -0.32, -0.32, 0.105, 1.0},
  }};

  std::string entity_name_;
  std::string service_name_;
  std::string command_topic_;
  double update_rate_;
  double max_horizontal_speed_;
  double max_vertical_speed_;
  double max_yaw_rate_;
  double command_timeout_;
  double min_z_;
  double idle_spin_rate_;
  double command_spin_boost_;
  double x_;
  double y_;
  double z_;
  double yaw_;
  std::array<double, 4> propeller_angles_;

  geometry_msgs::msg::Twist latest_command_;
  std::chrono::steady_clock::time_point last_command_wall_;
  std::chrono::steady_clock::time_point last_update_wall_;
  rclcpp::Client<gazebo_msgs::srv::SetEntityState>::SharedPtr state_client_;
  rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr cmd_sub_;
  rclcpp::TimerBase::SharedPtr timer_;
  std::unique_ptr<tf2_ros::TransformBroadcaster> tf_broadcaster_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<ManualDroneController>());
  rclcpp::shutdown();
  return 0;
}
