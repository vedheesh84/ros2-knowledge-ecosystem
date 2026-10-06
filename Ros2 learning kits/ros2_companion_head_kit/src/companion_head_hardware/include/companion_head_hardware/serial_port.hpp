// Copyright (c) 2024 ROS2 Learning Kit
// MIT License

#ifndef COMPANION_HEAD_HARDWARE__SERIAL_PORT_HPP_
#define COMPANION_HEAD_HARDWARE__SERIAL_PORT_HPP_

#include <string>
#include <termios.h>

namespace companion_head_hardware
{

class SerialPort
{
public:
  SerialPort();
  ~SerialPort();

  bool open(const std::string & port, int baud);
  void close();
  bool is_open() const;
  int write(const std::string & data);
  std::string read_line();
  void flush();

private:
  int fd_;
  struct termios tty_old_;
  std::string read_buffer_;

  speed_t get_baud_rate(int baud);
};

}  // namespace companion_head_hardware

#endif  // COMPANION_HEAD_HARDWARE__SERIAL_PORT_HPP_
