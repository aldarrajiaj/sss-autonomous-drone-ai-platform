#!/bin/bash

echo "Starting SSS Autonomous Drone AI Platform..."
cd ~/drone_project
uvicorn web_app:app --reload
