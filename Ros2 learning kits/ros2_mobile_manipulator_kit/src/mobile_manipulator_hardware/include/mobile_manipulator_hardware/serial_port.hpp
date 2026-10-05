// Copyright (c) 2024 ROS2 Learning Kit
// MIT License

#ifndef MOBILE_MANIPULATOR_HARDWARE__SERIAL_PORT_HPP_
#define MOBILE_MANIPULATOR_HARDWARE__SERIAL_PORT_HPP_

/**
 * @file serial_port.hpp
 * @brief Simple serial port wrapper for hardware communication
 *
 * LEARNING OBJECTIVES:
 * - Understand serial communication basics
 * - See POSIX termios API usage
 * - Learn non-blocking read patterns
 */

#include <string>
#include <termios.h>

namespace mobile_manipulator_hardware
{

class SerialPort
{
public:
  SerialPort();
  ~SerialPort();

  /**
   * @brief Open serial port
   * @param port Device path (e.g., /dev/ttyACM0)
   * @param baud Baud rate (e.g., 115200)
   * @return true if successful
   */
  bool open(const std::string & port, int baud);

  /**
   * @brief Close serial port
   */
  void close();

  /**
   * @brief Check if port is open
   */
  bool is_open() const;

  /**
   * @brief Write data to port
   * @param data String to write
   * @return Number of bytes written
   */
  int write(const std::string & data);

  /**
   * @brief Read line from port (non-blocking)
   * @return Line read (empty if none available)
   */
  std::string read_line();

  /**
   * @brief Flush input/output buffers
   */
  void flush();

private:
  int fd_;
  struct termios tty_old_;
  std::string read_buffer_;

  speed_t get_baud_rate(int baud);
};

}  // namespace mobile_manipulator_hardware

#endif  // MOBILE_MANIPULATOR_HARDWARE__SERIAL_PORT_HPP_
