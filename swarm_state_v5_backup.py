# Version 5: Dynamic Swarm Fleet Management
# Centralized simulation-only swarm state.
# This file does not send commands to real drones.

VALID_DRONE_ROLES = ["leader", "follower", "reserve"]


def create_drone_record(drone_number, role="follower"):
    """
    Create one simulation-only drone record.
    No real MAVSDK or hardware command is sent from this file.
    """
    if role not in VALID_DRONE_ROLES:
        role = "follower"

    return {
        "drone_id": f"SSS-DRONE-{drone_number:02d}",
        "nav_sys_id": drone_number,
        "connected": False,
        "armed": False,
        "in_air": False,
        "altitude": 0,
        "battery": "SIM",
        "mission_state": "idle",
        "formation": "none",
        "selected": False,
        "role": role,
    }


# Default Version 5 starting fleet.
# We keep 5 drones at startup, but the fleet can grow or shrink dynamically later.
swarm_fleet = {
    1: create_drone_record(1, "leader"),
    2: create_drone_record(2, "follower"),
    3: create_drone_record(3, "follower"),
    4: create_drone_record(4, "follower"),
    5: create_drone_record(5, "reserve"),
}


swarm_status = {
    "mode": "simulation",
    "total_drones": len(swarm_fleet),
    "selected_drones": [],
    "message": "Version 5 dynamic swarm fleet initialized in simulation mode",
}
