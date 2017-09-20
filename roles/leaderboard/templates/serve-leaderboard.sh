#! /bin/bash
cd {{ansible_env.HOME}}/leaderboard/build
python -m SimpleHTTPServer {{leaderboard_port}}