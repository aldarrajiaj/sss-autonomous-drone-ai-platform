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

---

## Version 3 — Swarm Control Foundation

Version 3 begins the transition from a single-drone command dashboard into the SSS AI Swarm Drone Software platform. This version is still simulation-first and does not send real swarm flight commands to physical drones.

The goal of Version 3 is to build the software foundation for future 5-to-50 drone swarm operations while keeping all testing safe inside simulation.

### Version 3 Features

- Professional SSS AI Swarm Drone Software dashboard
- Simulation-only 5-drone swarm fleet panel
- Drone ID and MAV_SYS_ID display
- Per-drone status tracking:
  - Connected
  - Armed
  - In Air
  - Altitude
  - Battery placeholder
  - Mission state
  - Formation state
  - Selection state
- Select single drone
- Select all drones
- Clear drone selection
- Emergency land selected drone simulation
- Emergency land all drones simulation
- Staggered takeoff simulation
- Formation hold simulation
- Swarm mission status display
- Safe backend API routes for swarm state management

### Version 3 Backend Routes

- `GET /swarm_status`
- `POST /select_drone`
- `POST /select_all_drones`
- `POST /clear_selection`
- `POST /emergency_land_selected`
- `POST /emergency_land_all`
- `POST /staggered_takeoff_sim`
- `POST /formation_hold_sim`
- `GET /swarm_dashboard`

### Version 3 Safety Note

All Version 3 swarm actions are simulation-only. The emergency land, staggered takeoff, and formation hold functions update the simulated software state only. They do not send real MAVSDK, MAVLink, PX4, or physical drone flight commands.

QGroundControl may still be used later as a temporary safety and setup tool during real drone testing, but the long-term goal is to continue building the company-owned SSS AI Swarm Drone Software platform.

### Version 3 Screenshots

#### Select Drone Test

![Select Drone Test](screenshots/version3/02_select_drone_test.png)

#### Select All Test

![Select All Test](screenshots/version3/03_select_all_test.png)

#### Clear Selection Test

![Clear Selection Test](screenshots/version3/04_clear_selection_test.png)

#### Staggered Takeoff Simulation

![Staggered Takeoff Simulation](screenshots/version3/05_staggered_takeoff_sim.png)

#### Formation Hold Simulation

![Formation Hold Simulation](screenshots/version3/06_formation_hold_sim.png)

#### Emergency Land All Simulation

![Emergency Land All Simulation](screenshots/version3/07_emergency_land_all.png)

