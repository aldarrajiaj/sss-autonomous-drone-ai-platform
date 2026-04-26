#!/bin/bash

echo "Starting PX4 SITL gz_x500 in HEADLESS mode..."
cd ~/PX4-Autopilot
make px4_sitl gz_x500 HEADLESS=1

