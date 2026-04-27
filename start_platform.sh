#!/bin/bash

echo "Starting SSS Autonomous Drone AI Platform..."
cd ~/sss_autonomous_drone_ai_platform
uvicorn web_app:app --reload
