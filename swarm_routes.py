# Version 4 - Swarm Architecture Upgrade
# Swarm API routes separated from the main web_app.py file.
# These routes are simulation-only and do not send commands to real drones.

from fastapi import APIRouter
from swarm_state import (
    swarm_fleet,
    swarm_status,
    create_drone_record,
    VALID_DRONE_ROLES,
    VALID_MISSION_TYPES,
    VALID_FORMATIONS,
)
router = APIRouter()


@router.post("/assign_simulated_mission")
async def assign_simulated_mission(
    mission_type: str = "surveillance",
    formation: str = "line",
):
    """
    Assign a simulation-only swarm mission.
    This does not send commands to real drones.
    """
    if mission_type not in VALID_MISSION_TYPES:
        mission_type = "surveillance"

    if formation not in VALID_FORMATIONS:
        formation = "line"

    if len(swarm_status["selected_drones"]) > 0:
        target_drones = swarm_status["selected_drones"]
    else:
        target_drones = list(swarm_fleet.keys())

    for index, drone_number in enumerate(target_drones, start=1):
        if drone_number in swarm_fleet:
            swarm_fleet[drone_number]["mission_state"] = "assigned"
            swarm_fleet[drone_number]["mission_progress"] = 0
            swarm_fleet[drone_number]["mission_type"] = mission_type
            swarm_fleet[drone_number]["formation"] = formation
            swarm_fleet[drone_number]["formation_position"] = f"{formation}-{index}"

    swarm_status["active_mission_type"] = mission_type
    swarm_status["active_formation"] = formation
    swarm_status["mission_progress"] = 0
    swarm_status["mission_state"] = "assigned"
    swarm_status["message"] = (
        f"Assigned {mission_type} mission using {formation} formation "
        f"to {len(target_drones)} simulated drone(s)"
    )

    return {
        "status": "mission_assigned",
        "message": swarm_status["message"],
        "target_drones": target_drones,
        "swarm_status": swarm_status,
        "fleet": list(swarm_fleet.values()),
    }


@router.post("/start_simulated_mission")
async def start_simulated_mission():
    """
    Start the currently assigned simulation-only swarm mission.
    This does not send commands to real drones.
    """
    if swarm_status["mission_state"] != "assigned":
        swarm_status["message"] = "No assigned mission is ready to start"
        return {
            "status": "failed",
            "message": swarm_status["message"],
            "swarm_status": swarm_status,
            "fleet": list(swarm_fleet.values()),
        }

    active_drones = []

    for drone_number, drone in swarm_fleet.items():
        if drone["mission_state"] == "assigned":
            drone["mission_state"] = "in_progress"
            drone["mission_progress"] = 25
            drone["in_air"] = True
            drone["altitude"] = 10
            active_drones.append(drone_number)

    swarm_status["mission_state"] = "in_progress"
    swarm_status["mission_progress"] = 25
    swarm_status["message"] = (
        f"Started simulated {swarm_status['active_mission_type']} mission "
        f"with {len(active_drones)} drone(s)"
    )

    return {
        "status": "mission_started",
        "message": swarm_status["message"],
        "active_drones": active_drones,
        "swarm_status": swarm_status,
        "fleet": list(swarm_fleet.values()),
    }


@router.post("/advance_simulated_mission")
async def advance_simulated_mission():
    """
    Advance the current simulation-only swarm mission.
    This does not send commands to real drones.
    """
    if swarm_status["mission_state"] != "in_progress":
        swarm_status["message"] = "No simulated mission is currently in progress"
        return {
            "status": "failed",
            "message": swarm_status["message"],
            "swarm_status": swarm_status,
            "fleet": list(swarm_fleet.values()),
        }

    new_progress = min(swarm_status["mission_progress"] + 25, 100)
    swarm_status["mission_progress"] = new_progress

    completed_drones = []

    for drone_number, drone in swarm_fleet.items():
        if drone["mission_state"] == "in_progress":
            drone["mission_progress"] = new_progress

            if new_progress >= 100:
                drone["mission_state"] = "completed"
                drone["in_air"] = False
                drone["altitude"] = 0
                completed_drones.append(drone_number)

    if new_progress >= 100:
        swarm_status["mission_state"] = "completed"
        swarm_status["message"] = "Simulated swarm mission completed"
        route_status = "mission_completed"
    else:
        swarm_status["message"] = f"Simulated swarm mission advanced to {new_progress}%"
        route_status = "mission_advanced"

    return {
        "status": route_status,
        "message": swarm_status["message"],
        "mission_progress": swarm_status["mission_progress"],
        "completed_drones": completed_drones,
        "swarm_status": swarm_status,
        "fleet": list(swarm_fleet.values()),
    }

@router.post("/add_drone")
async def add_drone(role: str = "follower"):
    """
    Add one new simulation-only drone to the swarm fleet.
    This does not send commands to real drones.
    """
    if role not in VALID_DRONE_ROLES:
        role = "follower"

    if len(swarm_fleet) == 0:
        new_drone_number = 1
    else:
        new_drone_number = max(swarm_fleet.keys()) + 1

    swarm_fleet[new_drone_number] = create_drone_record(new_drone_number, role)

    swarm_status["total_drones"] = len(swarm_fleet)
    swarm_status["message"] = f"Added {swarm_fleet[new_drone_number]['drone_id']} as {role}"

    return {
        "status": "drone_added",
        "message": swarm_status["message"],
        "total_drones": swarm_status["total_drones"],
        "new_drone": swarm_fleet[new_drone_number],
        "fleet": list(swarm_fleet.values()),
    }

@router.post("/remove_drone")
async def remove_drone(drone_number: int):
    """
    Remove one simulation-only drone from the swarm fleet.
    This does not send commands to real drones.
    """
    if drone_number not in swarm_fleet:
        swarm_status["message"] = f"Drone {drone_number} not found in swarm"
        return {
            "status": "failed",
            "message": swarm_status["message"],
            "total_drones": len(swarm_fleet),
            "fleet": list(swarm_fleet.values()),
        }

    removed_drone = swarm_fleet.pop(drone_number)

    if drone_number in swarm_status["selected_drones"]:
        swarm_status["selected_drones"].remove(drone_number)

    swarm_status["total_drones"] = len(swarm_fleet)
    swarm_status["message"] = f"Removed {removed_drone['drone_id']} from swarm"

    return {
        "status": "drone_removed",
        "message": swarm_status["message"],
        "total_drones": swarm_status["total_drones"],
        "removed_drone": removed_drone,
        "selected_drones": swarm_status["selected_drones"],
        "fleet": list(swarm_fleet.values()),
    }

@router.get("/swarm_status")
async def get_swarm_status():
    fleet_list = list(swarm_fleet.values())

    health_summary = {
        "total_drones": len(fleet_list),
        "leader_count": sum(1 for drone in fleet_list if drone["role"] == "leader"),
        "follower_count": sum(1 for drone in fleet_list if drone["role"] == "follower"),
        "reserve_count": sum(1 for drone in fleet_list if drone["role"] == "reserve"),
        "selected_count": len(swarm_status["selected_drones"]),
        "in_air_count": sum(1 for drone in fleet_list if drone["in_air"] is True),
        "connected_count": sum(1 for drone in fleet_list if drone["connected"] is True),
        "simulation_only": True,
    }

    swarm_status["total_drones"] = health_summary["total_drones"]

    return {
        "swarm_status": swarm_status,
        "health_summary": health_summary,
        "fleet": fleet_list,
    }


@router.post("/select_drone")
async def select_drone(drone_number: int):
    if drone_number not in swarm_fleet:
        swarm_status["message"] = f"Drone {drone_number} not found in swarm"
        return {
            "status": "failed",
            "message": swarm_status["message"],
            "selected_drones": swarm_status["selected_drones"]
        }

    for drone in swarm_fleet.values():
        drone["selected"] = False

    swarm_fleet[drone_number]["selected"] = True
    swarm_status["selected_drones"] = [drone_number]
    swarm_status["message"] = f"Selected {swarm_fleet[drone_number]['drone_id']}"

    return {
        "status": "drone_selected",
        "message": swarm_status["message"],
        "selected_drones": swarm_status["selected_drones"],
        "drone": swarm_fleet[drone_number]
    }


@router.post("/select_all_drones")
async def select_all_drones():
    for drone in swarm_fleet.values():
        drone["selected"] = True

    swarm_status["selected_drones"] = list(swarm_fleet.keys())
    swarm_status["message"] = "All swarm drones selected"

    return {
        "status": "all_drones_selected",
        "message": swarm_status["message"],
        "selected_drones": swarm_status["selected_drones"],
        "fleet": list(swarm_fleet.values())
    }


@router.post("/clear_selection")
async def clear_selection():
    for drone in swarm_fleet.values():
        drone["selected"] = False

    swarm_status["selected_drones"] = []
    swarm_status["message"] = "Swarm drone selection cleared"

    return {
        "status": "selection_cleared",
        "message": swarm_status["message"],
        "selected_drones": swarm_status["selected_drones"],
        "fleet": list(swarm_fleet.values())
    }


@router.post("/emergency_land_selected")
async def emergency_land_selected():
    selected = swarm_status["selected_drones"]

    if len(selected) == 0:
        swarm_status["message"] = "No drone selected for emergency landing"
        return {
            "status": "failed",
            "message": swarm_status["message"],
            "selected_drones": selected,
            "fleet": list(swarm_fleet.values())
        }

    for drone_number in selected:
        if drone_number in swarm_fleet:
            swarm_fleet[drone_number]["armed"] = False
            swarm_fleet[drone_number]["in_air"] = False
            swarm_fleet[drone_number]["altitude"] = 0
            swarm_fleet[drone_number]["mission_state"] = "emergency_landed"

    swarm_status["message"] = "Emergency land command sent to selected simulated drone(s)"

    return {
        "status": "emergency_land_selected",
        "message": swarm_status["message"],
        "selected_drones": selected,
        "fleet": list(swarm_fleet.values())
    }


@router.post("/emergency_land_all")
async def emergency_land_all():
    for drone in swarm_fleet.values():
        drone["armed"] = False
        drone["in_air"] = False
        drone["altitude"] = 0
        drone["mission_state"] = "emergency_landed"

    swarm_status["selected_drones"] = list(swarm_fleet.keys())
    swarm_status["message"] = "Emergency land command sent to all simulated swarm drones"

    for drone in swarm_fleet.values():
        drone["selected"] = True

    return {
        "status": "emergency_land_all",
        "message": swarm_status["message"],
        "selected_drones": swarm_status["selected_drones"],
        "fleet": list(swarm_fleet.values())
    }


@router.post("/staggered_takeoff_sim")
async def staggered_takeoff_sim():
    base_altitude = 10

    for index, drone_number in enumerate(swarm_fleet.keys()):
        target_altitude = base_altitude + (index * 2)

        swarm_fleet[drone_number]["connected"] = True
        swarm_fleet[drone_number]["armed"] = True
        swarm_fleet[drone_number]["in_air"] = True
        swarm_fleet[drone_number]["altitude"] = target_altitude
        swarm_fleet[drone_number]["mission_state"] = "staggered_takeoff_complete"

    swarm_status["selected_drones"] = list(swarm_fleet.keys())
    swarm_status["message"] = "Staggered takeoff simulation completed for all swarm drones"

    for drone in swarm_fleet.values():
        drone["selected"] = True

    return {
        "status": "staggered_takeoff_complete",
        "message": swarm_status["message"],
        "selected_drones": swarm_status["selected_drones"],
        "fleet": list(swarm_fleet.values())
    }


@router.post("/formation_hold_sim")
async def formation_hold_sim():
    for drone_number, drone in swarm_fleet.items():
        drone["connected"] = True
        drone["armed"] = True
        drone["in_air"] = True

        if drone["altitude"] == 0:
            drone["altitude"] = 10

        drone["mission_state"] = "formation_hold"
        drone["formation"] = "square_grid_hold"
        drone["selected"] = True

    swarm_status["selected_drones"] = list(swarm_fleet.keys())
    swarm_status["message"] = "Formation hold simulation active in square grid pattern"

    return {
        "status": "formation_hold_active",
        "message": swarm_status["message"],
        "selected_drones": swarm_status["selected_drones"],
        "fleet": list(swarm_fleet.values())
    }
