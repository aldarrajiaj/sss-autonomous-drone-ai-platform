# Version 4 - Swarm Architecture Upgrade
# Centralized simulation-only swarm state.
# This file does not send commands to real drones.

swarm_fleet = {
    1: {
        "drone_id": "SSS-DRONE-01",
        "mav_sys_id": 1,
        "connected": False,
        "armed": False,
        "in_air": False,
        "altitude": 0,
        "battery": "SIM",
        "mission_state": "idle",
        "formation": "none",
        "selected": False
    },
    2: {
        "drone_id": "SSS-DRONE-02",
        "mav_sys_id": 2,
        "connected": False,
        "armed": False,
        "in_air": False,
        "altitude": 0,
        "battery": "SIM",
        "mission_state": "idle",
        "formation": "none",
        "selected": False
    },
    3: {
        "drone_id": "SSS-DRONE-03",
        "mav_sys_id": 3,
        "connected": False,
        "armed": False,
        "in_air": False,
        "altitude": 0,
        "battery": "SIM",
        "mission_state": "idle",
        "formation": "none",
        "selected": False
    },
    4: {
        "drone_id": "SSS-DRONE-04",
        "mav_sys_id": 4,
        "connected": False,
        "armed": False,
        "in_air": False,
        "altitude": 0,
        "battery": "SIM",
        "mission_state": "idle",
        "formation": "none",
        "selected": False
    },
    5: {
        "drone_id": "SSS-DRONE-05",
        "mav_sys_id": 5,
        "connected": False,
        "armed": False,
        "in_air": False,
        "altitude": 0,
        "battery": "SIM",
        "mission_state": "idle",
        "formation": "none",
        "selected": False
    }
}

swarm_status = {
    "mode": "simulation",
    "total_drones": 5,
    "selected_drones": [],
    "message": "Swarm Control Foundation initialized in simulation mode"
}
