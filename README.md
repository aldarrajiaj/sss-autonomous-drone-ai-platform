# SSS Autonomous Drone AI Platform

## Project Overview

The SSS Autonomous Drone AI Platform is a browser-based drone command, telemetry, and emergency recovery interface designed to support multiple autonomous drone categories, including multirotor, fixed-wing, and VTOL platforms.

The current version runs in a PX4 SITL simulation environment and connects through FastAPI, MAVSDK, and MAVLink. The platform provides a clean operator dashboard for monitoring drone status, selecting drone control profiles, sending mission commands, tracking command history, viewing altitude data, and using emergency recovery controls.

The long-term goal is to connect this platform to SSS-built drone hardware using PX4 or ArduPilot-compatible flight controllers, MAVLink telemetry, secure communications, and operator-supervised autonomy.

## Key Features

- Browser-based drone command dashboard
- PX4 SITL simulation integration
- FastAPI backend
- MAVSDK / MAVLink drone communication
- Live drone connection status
- Mission state indicator
- Live telemetry display
- Command history panel
- Altitude monitor with visual bar
- Emergency recovery panel
- Operational safety section
- Dynamic drone mode selector
- Multirotor, fixed-wing, and VTOL control profiles
- Startup scripts for PX4 and the web platform

## Supported Drone Modes

### Multirotor Mode

Designed for vertical takeoff and landing drones.

Controls shown:

- Arm Drone
- Launch Drone
- Hover Forward
- Land Drone
- Hold Position

### Fixed-Wing Mode

Designed for future fixed-wing autonomous drone platforms.

Controls shown:

- Arm System
- Launch Sequence
- Start Mission
- Return to Base
- Loiter Area

### VTOL Mode

Designed for future vertical takeoff and transition-flight drone platforms.

Controls shown:

- Arm System
- Vertical Takeoff
- Transition Flight
- Vertical Landing
- Mission Hold

## System Architecture

The current simulation workflow is:

Browser User Interface
        |
        v
FastAPI Web Server
        |
        v
MAVSDK Python
        |
        v
MAVLink
        |
        v
PX4 SITL Simulator
        |
        v
gz_x500 Drone Model

## Tools and Technologies

- Ubuntu 22.04
- Oracle VirtualBox
- PX4 Autopilot
- PX4 SITL
- Gazebo gz_x500 simulation model
- Python 3
- FastAPI
- Uvicorn
- MAVSDK
- MAVLink
- HTML/CSS browser dashboard
- Bash startup scripts

## Folder Structure

sss_autonomous_drone_ai_platform/
├── README.md
├── connect_test.py
├── takeoff_land.py
├── web_app.py
├── start_px4.sh
├── start_platform.sh
└── screenshots/

## How to Run the Platform

### 1. Start PX4 SITL

Open the first terminal:

cd ~/sss_autonomous_drone_ai_platform
./start_px4.sh

### 2. Start the Web Platform

Open the second terminal:

cd ~/sss_autonomous_drone_ai_platform
./start_platform.sh

### 3. Open the Dashboard

Open a browser and go to:

http://127.0.0.1:8000

## Screenshots

Project screenshots are stored in the screenshots/ folder. They show the dashboard, drone mode selector, telemetry indicators, command history, altitude monitor, safety controls, and PX4/Gazebo simulation environment.

## Current Status

This version has been tested in a PX4 SITL simulation environment using the gz_x500 drone model. The platform successfully connects to the drone simulator, displays live status information, and provides a browser-based control interface for simulated mission operations.

## Future Improvements

Planned improvements include:

- Real drone hardware integration
- GPS waypoint mission planning
- Obstacle detection support
- AI-assisted mission decision-making
- Secure remote operator access
- Flight log storage and review
- Role-based user authentication
- Integration with SSS drone hardware prototypes

## Author

Ammar Aldarraji  
U.S. Army Veteran | Cybersecurity Analyst | Drone AI / Autonomous Systems Portfolio Project
