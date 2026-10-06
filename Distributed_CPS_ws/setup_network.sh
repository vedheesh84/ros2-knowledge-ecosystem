#!/usr/bin/env bash
# ==============================================================================
# setup_network.sh: Automated Network Setup for Distributed Multi-Robot CPS
# Configures Chrony NTP Time Synchronization and FastDDS Discovery Server.
# ==============================================================================

set -e

ROLE=${1:-"client"}
BASE_IP=${2:-"192.168.1.100"}

echo "=== Configuring Distributed CPS Network: Role [$ROLE] ==="

if [ "$ROLE" = "server" ]; then
    echo "Configuring Base Station as Chrony NTP Master Server..."
    sudo apt-get update && sudo apt-get install -y chrony
    sudo tee /etc/chrony/chrony.conf > /dev/null << 'EOF'
server pool.ntp.org iburst
allow 192.168.1.0/24
local stratum 10
EOF
    sudo systemctl restart chrony
    echo "Starting FastDDS Discovery Server on UDP:11811 (FastDDS Default)..."
    fastdds discovery -i 0 -p 11811 &
    export FASTRTPS_DEFAULT_PROFILES_FILE="$(pwd)/src/cps_bringup/config/fastdds_discovery_server.xml"
    echo "Base Station configuration complete."

elif [ "$ROLE" = "client" ]; then
    echo "Configuring Edge Robot as Chrony NTP Client syncing to Base Station [$BASE_IP]..."
    sudo apt-get update && sudo apt-get install -y chrony
    sudo tee /etc/chrony/chrony.conf > /dev/null << EOF
server $BASE_IP iburst minpoll 2 maxpoll 4
makestep 0.1 3
EOF
    sudo systemctl restart chrony
    export ROS_DISCOVERY_SERVER="$BASE_IP:11811"
    export FASTRTPS_DEFAULT_PROFILES_FILE="$(pwd)/src/cps_bringup/config/fastdds_discovery_server.xml"
    echo "Edge Robot network configuration complete."
else
    echo "Usage: ./setup_network.sh [server|client] [BASE_IP]"
    exit 1
fi
