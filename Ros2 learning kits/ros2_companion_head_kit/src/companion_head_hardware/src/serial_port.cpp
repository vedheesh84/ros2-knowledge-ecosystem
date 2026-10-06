// Copyright (c) 2024 ROS2 Learning Kit
// MIT License

#include "companion_head_hardware/serial_port.hpp"

#include <fcntl.h>
#include <unistd.h>
#include <cstring>

namespace companion_head_hardware
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
  fd_ = ::open(port.c_str(), O_RDWR | O_NOCTTY | O_NONBLOCK);
  if (fd_ < 0) {
    return false;
  }

  tcgetattr(fd_, &tty_old_);

  struct termios tty;
  memset(&tty, 0, sizeof(tty));

  speed_t baud_rate = get_baud_rate(baud);
  cfsetispeed(&tty, baud_rate);
  cfsetospeed(&tty, baud_rate);

  tty.c_cflag |= (CLOCAL | CREAD);
  tty.c_cflag &= ~PARENB;
  tty.c_cflag &= ~CSTOPB;
  tty.c_cflag &= ~CSIZE;
  tty.c_cflag |= CS8;
  tty.c_cflag &= ~CRTSCTS;

  tty.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG);
  tty.c_oflag &= ~OPOST;
  tty.c_iflag &= ~(IXON | IXOFF | IXANY);

  tty.c_cc[VMIN] = 0;
  tty.c_cc[VTIME] = 0;

  if (tcsetattr(fd_, TCSANOW, &tty) != 0) {
    ::close(fd_);
    fd_ = -1;
    return false;
  }

  flush();
  return true;
}

void SerialPort::close()
{
  if (fd_ >= 0) {
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
  if (!is_open()) {
    return -1;
  }
  return ::write(fd_, data.c_str(), data.length());
}

std::string SerialPort::read_line()
{
  if (!is_open()) {
    return "";
  }

  char buf[256];
  int bytes_read = ::read(fd_, buf, sizeof(buf) - 1);

  if (bytes_read > 0) {
    buf[bytes_read] = '\0';
    read_buffer_ += buf;
  }

  size_t newline_pos = read_buffer_.find('\n');
  if (newline_pos != std::string::npos) {
    std::string line = read_buffer_.substr(0, newline_pos);
    read_buffer_.erase(0, newline_pos + 1);
    if (!line.empty() && line.back() == '\r') {
      line.pop_back();
    }
    return line;
  }

  return "";
}

void SerialPort::flush()
{
  if (is_open()) {
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
    case 921600: return B921600;
    default: return B115200;
  }
}

}  // namespace companion_head_hardware
