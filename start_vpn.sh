tmux new-session -d -s ovpn
tmux send-keys -t ovpn.0 '/home/pi/sniffer/start_vpn_config.sh' ENTER