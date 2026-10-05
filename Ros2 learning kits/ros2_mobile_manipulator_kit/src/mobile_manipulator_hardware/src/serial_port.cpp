// Copyright (c) 2024 ROS2 Learning Kit
// MIT License

/**
 * @file serial_port.cpp
 * @brief Serial port implementation
 *
 * LEARNING OBJECTIVES:
 * - Understand POSIX serial port API (termios)
 * - See non-blocking read implementation
 * - Learn buffer management for line-based protocol
 */

#include "mobile_manipulator_hardware/serial_port.hpp"

#include <fcntl.h>
#include <unistd.h>
#include <cstring>

namespace mobile_manipulator_hardware
{

SerialPort::SerialPort()
: fd_(-1)
{
}

SerialPort::~SerialPort()
{
  close();
}

bool SerialPort::open(const std::string & port, int baud)
{
  // Open port
  fd_ = ::open(port.c_str(), O_RDWR | O_NOCTTY | O_NONBLOCK);
  if (fd_ < 0) {
    return false;
  }

  // Save old settings
  tcgetattr(fd_, &tty_old_);

  // Configure port
  struct termios tty;
  memset(&tty, 0, sizeof(tty));

  // Set baud rate
  speed_t baud_rate = get_baud_rate(baud);
  cfsetispeed(&tty, baud_rate);
  cfsetospeed(&tty, baud_rate);

  // 8N1 (8 data bits, no parity, 1 stop bit)
  tty.c_cflag |= (CLOCAL | CREAD);
  tty.c_cflag &= ~PARENB;
  tty.c_cflag &= ~CSTOPB;
  tty.c_cflag &= ~CSIZE;
  tty.c_cflag |= CS8;

  // No hardware flow control
  tty.c_cflag &= ~CRTSCTS;

  // Raw input
  tty.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG);

  // Raw output
  tty.c_oflag &= ~OPOST;

  // No software flow control
  tty.c_iflag &= ~(IXON | IXOFF | IXANY);

  // Non-blocking read
  tty.c_cc[VMIN] = 0;
  tty.c_cc[VTIME] = 0;

  // Apply settings
  if (tcsetattr(fd_, TCSANOW, &tty) != 0) {
    ::close(fd_);
    fd_ = -1;
    return false;
  }

  // Flush buffers
  flush();

  return true;
}

void SerialPort::close()
{
  if (fd_ >= 0) {
    // Restore old settings
    tcsetattr(fd_, TCSANOW, &tty_old_);
    ::close(fd_);
    fd_ = -1;
  }
  read_buffer_.clear();
}

bool SerialPort::is_open() const
{
  return fd_ >= 0;
}

int SerialPort::write(const std::string & data)
{
  if (fd_ < 0) {
    return -1;
  }
  return ::write(fd_, data.c_str(), data.length());
}

std::string SerialPort::read_line()
{
  if (fd_ < 0) {
    return "";
  }

  // Read available data
  char buf[256];
  int n = ::read(fd_, buf, sizeof(buf) - 1);
  if (n > 0) {
    buf[n] = '\0';
    read_buffer_ += buf;
  }

  // Check for complete line
  size_t pos = read_buffer_.find('\n');
  if (pos != std::string::npos) {
    std::string line = read_buffer_.substr(0, pos);
    read_buffer_.erase(0, pos + 1);

    // Remove carriage return if present
    if (!line.empty() && line.back() == '\r') {
      line.pop_back();
    }
    return line;
  }

  return "";
}

void SerialPort::flush()
{
  if (fd_ >= 0) {
    tcflush(fd_, TCIOFLUSH);
  }
  read_buffer_.clear();
}

speed_t SerialPort::get_baud_rate(int baud)
{
  switch (baud) {
    case 9600: return B9600;
    case 19200: return B19200;
    case 38400: return B38400;
    case 57600: return B57600;
    case 115200: return B115200;
    case 230400: return B230400;
    case 460800: return B460800;
    default: return B115200;
  }
}

}  // namespace mobile_manipulator_hardware
