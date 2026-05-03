import asyncio
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from mavsdk import System
from mavsdk.offboard import VelocityBodyYawspeed
from swarm_routes import router as swarm_router

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(swarm_router)
drone = System()
telemetry_data = {
    "connected": False,
    "armed": False,
    "in_air": False,
    "altitude": 0
}

@app.get("/swarm_dashboard_v4", response_class=HTMLResponse)
async def swarm_dashboard_v4():
    with open("templates/swarm_dashboard.html", "r") as file:
        return file.read()

mission_waypoints = []
mission_state = {
    "uploaded": False,
    "started": False,
    "message": "No mission loaded"
}

# Version 3 - Swarm Control Foundation
# Simulation-only fleet state for safe swarm software development.
# This does not send commands to real drones.
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
@app.on_event("startup")
async def startup():
    print("Starting background drone connection task...")

    async def connect_and_track():
        try:
            print("Connecting to drone...")
            await drone.connect(system_address="udp://:14540")

            async for state in drone.core.connection_state():
                if state.is_connected:
                    print("Drone connected!")
                    telemetry_data["connected"] = True
                    break

            async def track_armed():
                async for is_armed in drone.telemetry.armed():
                    telemetry_data["armed"] = is_armed

            async def track_in_air():
                async for in_air in drone.telemetry.in_air():
                    telemetry_data["in_air"] = in_air

            async def track_altitude():
                async for position in drone.telemetry.position():
                    telemetry_data["altitude"] = round(position.relative_altitude_m, 2)

            asyncio.create_task(track_armed())
            asyncio.create_task(track_in_air())
            asyncio.create_task(track_altitude())

        except Exception as e:
            print(f"Drone connection background task error: {e}")
            telemetry_data["connected"] = False

    asyncio.create_task(connect_and_track())
    print("Web platform startup complete. Drone connection will continue in background.")


@app.get("/arm")
async def arm():
    print("Arming...")
    await drone.action.arm()
    return {"status": "armed"}


@app.get("/takeoff")
async def takeoff():
    print("Arming before takeoff...")
    await drone.action.arm()

    print("Taking off...")
    await drone.action.takeoff()

    return {"status": "takeoff"}

@app.get("/land")
async def land():
    print("Landing...")
    await drone.action.land()
    return {"status": "landing"}


from fastapi.responses import HTMLResponse

@app.post("/add_waypoint")
async def add_waypoint(latitude: float, longitude: float, altitude: float):
    waypoint = {
        "latitude": latitude,
        "longitude": longitude,
        "altitude": altitude
    }
    mission_waypoints.append(waypoint)
    mission_state["message"] = f"Waypoint added: {latitude}, {longitude}, {altitude}m"
    return {
        "status": "waypoint_added",
        "waypoint": waypoint,
        "total_waypoints": len(mission_waypoints)
    }


@app.post("/clear_mission")
async def clear_mission():
    mission_waypoints.clear()
    mission_state["uploaded"] = False
    mission_state["started"] = False
    mission_state["message"] = "Mission cleared"
    return {
        "status": "mission_cleared",
        "total_waypoints": len(mission_waypoints)
    }


@app.get("/mission_status")
async def mission_status():
    return {
        "waypoints": mission_waypoints,
        "mission_state": mission_state
    }


@app.get("/swarm_status")
async def get_swarm_status():
    return {
        "swarm_status": swarm_status,
        "fleet": list(swarm_fleet.values())
    }

@app.post("/select_drone")
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

@app.post("/select_all_drones")
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

@app.post("/clear_selection")
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

@app.post("/emergency_land_selected")
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

@app.post("/emergency_land_all")
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

@app.post("/staggered_takeoff_sim")
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

@app.post("/formation_hold_sim")
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

@app.post("/upload_mission")
async def upload_mission():
    if len(mission_waypoints) == 0:
        mission_state["uploaded"] = False
        mission_state["message"] = "Cannot upload mission: no waypoints added"
        return {
            "status": "failed",
            "message": mission_state["message"]
        }

    mission_state["uploaded"] = True
    mission_state["started"] = False
    mission_state["message"] = f"Mission uploaded with {len(mission_waypoints)} waypoint(s)"
    return {
        "status": "mission_uploaded",
        "total_waypoints": len(mission_waypoints),
        "waypoints": mission_waypoints
    }


@app.post("/start_mission")
async def start_mission():
    if not mission_state["uploaded"]:
        mission_state["message"] = "Cannot start mission: mission not uploaded"
        return {
            "status": "failed",
            "message": mission_state["message"]
        }

    mission_state["started"] = True
    mission_state["message"] = "Mission started in simulation mode"
    return {
        "status": "mission_started",
        "message": mission_state["message"],
        "waypoints": mission_waypoints
    }

@app.get("/control", response_class=HTMLResponse)
def control_ui():
    return """
    <html>
    <head>
        <title>SSS Drone Control</title>
    </head>
    <body>

    <h1>SSS Drone Control</h1>

    <h3 id="status">Status: Idle</h3>

    <button onclick="sendCommand('/arm')">ARM</button><br><br>
    <button onclick="sendCommand('/takeoff')">TAKEOFF</button><br><br>
    <button onclick="sendCommand('/forward')">FORWARD</button><br><br>
    <button onclick="sendCommand('/stop')">STOP</button><br><br>
    <button onclick="sendCommand('/land')">LAND</button>

    <script>
    function sendCommand(cmd) {
        fetch(cmd)
        .then(response => response.json())
        .then(data => {
            document.getElementById("status").innerText =
                "Status: " + data.status;
        });
    }
    </script>

<hr>

<h2>Mission Planner</h2>

<label>Latitude:</label>
<input id="missionLat" type="number" step="0.0001" value="38.8895">

<label>Longitude:</label>
<input id="missionLon" type="number" step="0.0001" value="-77.0353">

<label>Altitude (m):</label>
<input id="missionAlt" type="number" step="1" value="20">

<br><br>

<button onclick="addWaypoint()">Add Waypoint</button>
<button onclick="uploadMission()">Upload Mission</button>
<button onclick="startMission()">Start Mission</button>
<button onclick="clearMission()">Clear Mission</button>

<h3>Mission Status</h3>
<div id="missionStatus">No mission loaded</div>

<h3>Waypoint List</h3>
<pre id="waypointList">[]</pre>

<script>
async function addWaypoint() {
    const lat = document.getElementById("missionLat").value;
    const lon = document.getElementById("missionLon").value;
    const alt = document.getElementById("missionAlt").value;

    const response = await fetch(`/add_waypoint?latitude=${lat}&longitude=${lon}&altitude=${alt}`, {
        method: "POST"
    });

    const data = await response.json();
    document.getElementById("missionStatus").innerText = data.status;
    refreshMissionStatus();
}

async function uploadMission() {
    const response = await fetch("/upload_mission", {
        method: "POST"
    });

    const data = await response.json();
    document.getElementById("missionStatus").innerText = data.message || data.status;
    refreshMissionStatus();
}

async function startMission() {
    const response = await fetch("/start_mission", {
        method: "POST"
    });

    const data = await response.json();
    document.getElementById("missionStatus").innerText = data.message || data.status;
    refreshMissionStatus();
}

async function clearMission() {
    const response = await fetch("/clear_mission", {
        method: "POST"
    });

    const data = await response.json();
    document.getElementById("missionStatus").innerText = data.status;
    refreshMissionStatus();
}

async function refreshMissionStatus() {
    const response = await fetch("/mission_status");
    const data = await response.json();

    document.getElementById("missionStatus").innerText = data.mission_state.message;
    document.getElementById("waypointList").innerText = JSON.stringify(data.waypoints, null, 2);
}

setInterval(refreshMissionStatus, 2000);
refreshMissionStatus();
</script>

    </body>
    </html>
    """
@app.get("/forward")
async def forward():
    print("Moving forward...")

    await drone.offboard.set_velocity_body(
        VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0)
    )

    await drone.offboard.start()

    for _ in range(20):
        await drone.offboard.set_velocity_body(
            VelocityBodyYawspeed(1.0, 0.0, 0.0, 0.0)
        )
        await asyncio.sleep(0.3)

    return {"status": "moving forward"}




@app.get("/stop")
async def stop():
    print("Stopping movement...")

    try:
        await drone.offboard.set_velocity_body(
            VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0)
        )
        await drone.offboard.stop()
        print("Offboard stopped.")
    except Exception as e:
        print(f"Stop warning: {e}")

    return {"status": "stopped"}

@app.get("/status")
async def status():
    return telemetry_data

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Drone Control UI</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #111827;
                color: white;
                text-align: center;
                padding-top: 40px;
            }

            h1 {
                color: #38bdf8;
            }

            .button {
		width: 150px;
    		height: 60px;
    		margin: 10px;
    		font-size: 16px;
    		border: none;
    		border-radius: 8px;
    		cursor: pointer;
    		background-color: #2563eb;
    		color: white;
    		display: inline-flex;
    		align-items: center;
    		justify-content: center;
    		vertical-align: top;
    		white-space: normal;
    		line-height: 1.2;
           }
            .button:hover {
                background-color: #1d4ed8;
            }

            .danger {
                background-color: #dc2626;
            }

            .danger:hover {
                background-color: #b91c1c;
            }
#modeBox {
    margin-top: 20px;
    margin-bottom: 20px;
    background-color: #111827;
    border: 1px solid #38bdf8;
    padding: 18px;
    border-radius: 12px;
    display: inline-block;
    min-width: 520px;
    text-align: center;
    font-size: 15px;
}

.modeTitle {
    color: #38bdf8;
    font-size: 19px;
    font-weight: bold;
    margin-bottom: 12px;
}

.modeButton {
    width: 150px;
    height: 42px;
    margin: 6px;
    font-size: 15px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    background-color: #374151;
    color: white;
}

.modeButton:hover {
    background-color: #2563eb;
}

.modeButton.active {
    background-color: #2563eb;
    font-weight: bold;
}

#modeDescription {
    color: #dbeafe;
    margin-top: 12px;
    font-size: 14px;
}

           .indicatorRow {
    margin-top: 25px;
    margin-bottom: 20px;
}

.indicator {
    display: inline-block;
    background-color: #1f2937;
    border: 1px solid #374151;
    border-radius: 10px;
    padding: 12px 18px;
    margin: 5px;
    font-size: 16px;
}

.online {
    color: #22c55e;
    font-weight: bold;
}

.warningText {
    color: #facc15;
    font-weight: bold;
}
 #statusBox {
                margin-top: 30px;
                background-color: #1f2937;
                padding: 20px;
                border-radius: 10px;
                display: inline-block;
                min-width: 350px;
                text-align: left;
                font-size: 18px;
            }
.panelRow {
    display: flex;
    justify-content: center;
    align-items: stretch;
    gap: 10px;
    margin-top: 25px;
    flex-wrap: wrap;
}
#emergencyBox {
    margin-top: 0;
    background-color: #2b1111;
    border: 2px solid #dc2626;
    padding: 20px;
    border-radius: 12px;
    display: inline-block;
    width: 430px;
    height: 150px;
    vertical-align: top;
    text-align: center;
    font-size: 16px;
}

.emergencyTitle {
    color: #f87171;
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 10px;
}

.emergencyText {
    color: #fecaca;
    font-size: 15px;
    margin-bottom: 15px;
}

.emergencyButton {
    width: 220px;
    height: 55px;
    font-size: 18px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    background-color: #991b1b;
    color: white;
    font-weight: bold;
}

.emergencyButton:hover {
    background-color: #7f1d1d;
}
#safetyBox {
    margin-top: 0;
    background-color: #111827;
    border: 1px solid #facc15;
    padding: 18px;
    border-radius: 12px;
    display: inline-block;
    width: 430px;
    height: 150px;
    vertical-align: top;
    text-align: left;
    font-size: 15px;
}

.safetyTitle {
    color: #facc15;
    font-size: 19px;
    font-weight: bold;
    margin-bottom: 10px;
    text-align: center;
}

.safetyList {
    color: #fef3c7;
    line-height: 1.6;
}

#historyBox {
    margin-top: 0;
    background-color: #111827;
    border: 1px solid #38bdf8;
    padding: 18px;
    border-radius: 12px;
    display: inline-block;
    width: 430px;
    min-height: 130px;
    text-align: left;
    font-size: 15px;
}

.historyTitle {
    color: #38bdf8;
    font-size: 19px;
    font-weight: bold;
    margin-bottom: 10px;
    text-align: center;
}

#historyText {
    color: #dbeafe;
    white-space: pre-wrap;
}
#historyText {
    color: #dbeafe;
    white-space: pre-wrap;
}

#altitudeBox {
    margin-top: 0;
    background-color: #111827;
    border: 1px solid #22c55e;
    padding: 18px;
    border-radius: 12px;
    display: inline-block;
    width: 430px;
    text-align: left;
    font-size: 15px;
}
.altitudeTitle {
    color: #22c55e;
    font-size: 19px;
    font-weight: bold;
    margin-bottom: 10px;
    text-align: center;
}

.altitudeBarBackground {
    width: 100%;
    height: 22px;
    background-color: #374151;
    border-radius: 12px;
    overflow: hidden;
    margin-top: 10px;
}

#altitudeBar {
    height: 100%;
    width: 0%;
    background-color: #22c55e;
    transition: width 0.4s ease;
}

#altitudeValue {
    color: #d1fae5;
    font-weight: bold;
}
.missionPlannerBox {
    margin: 30px auto;
    max-width: 900px;
    background: #111827;
    border: 1px solid #38bdf8;
    border-radius: 12px;
    padding: 20px;
    color: white;
}

.missionTitle {
    color: #38bdf8;
    font-size: 22px;
    font-weight: bold;
    text-align: center;
    margin-bottom: 8px;
}

.missionSubtext {
    text-align: center;
    color: #cbd5e1;
    margin-bottom: 18px;
}

.missionInputs {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-bottom: 18px;
}

.missionInputs label {
    color: #facc15;
    font-weight: bold;
}

.missionInputs input {
    width: 100%;
    padding: 10px;
    border-radius: 8px;
    border: 1px solid #334155;
    background: #020617;
    color: white;
}

.missionButtons {
    display: flex;
    justify-content: center;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 18px;
}

.missionInfoGrid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
}

.missionInfoGrid pre {
    background: #020617;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 12px;
    min-height: 80px;
    color: #e5e7eb;
    white-space: pre-wrap;
}

        </style>
    </head>
    <body>
        <h1>SSS Autonomous Drone AI Platform</h1>
        <p>Autonomous Drone Command, Telemetry, and Emergency Recovery Interface</p>
	<p style="color:#facc15; font-weight:bold;">
   	    Safety: Take off before using movement controls. Use LAND for emergency recovery.
        </p>
<div id="modeBox">
    <div class="modeTitle">Platform Mode</div>

    <button id="modeMultirotor" class="modeButton active" onclick="setMode('Multirotor')">
        Multirotor
    </button>

    <button id="modeFixedWing" class="modeButton" onclick="setMode('Fixed-Wing')">
        Fixed-Wing
    </button>

    <button id="modeVTOL" class="modeButton" onclick="setMode('VTOL')">
        VTOL
    </button>

    <div id="modeDescription">
        Selected Mode: Multirotor<br>
        Control Profile: Vertical takeoff and landing drone
    </div>
</div>
<div class="indicatorRow">
    <div class="indicator">System: <span class="online">Online</span></div>
    <div class="indicator">Drone Link: <span id="px4Status" class="warningText">Checking...</span></div>
    <div class="indicator">Mission State: <span id="flightStatus" class="warningText">Ready</span></div>
</div>
        <div>
<button id="btnArm" class="button" onclick="sendCommand('/arm')">Arm Drone</button>
<button id="btnLaunch" class="button" onclick="sendCommand('/takeoff')">Launch Drone</button>
<button id="btnMove" class="button" onclick="sendCommand('/forward')">Move Forward</button>
<button id="btnLand" class="button danger" onclick="sendCommand('/land')">Land Drone</button>
<button id="btnStop" class="button danger" onclick="sendCommand('/stop')">Hold Position</button>
        </div>

<div id="statusBox">
    <strong>Status:</strong>
    <pre id="statusText">Loading...</pre>
</div>

<div id="logBox">
    <strong>Mission Log:</strong>
    <pre id="logText">Waiting for command...</pre>
</div>
<div class="panelRow">
<div id="emergencyBox">
    <div class="emergencyTitle">Emergency Recovery</div>
    <div class="emergencyText">
        Use this section only if the drone becomes unstable or must return to the ground.
    </div>
       <button class="emergencyButton" onclick="sendCommand('/land')">
          Emergency Land Drone
    </button>
</div>
<div id="safetyBox">
    <div class="safetyTitle">Operational Safety</div>
    <div class="safetyList">
        • Use TAKEOFF before movement commands.<br>
        • Use STOP before LAND after movement.<br>
        • Use EMERGENCY LAND if the drone becomes unstable.<br>
        • Monitor PX4 connection and flight status before sending commands.
        </div>
   </div>

 <div id="historyBox">
      <div class="historyTitle">Command History</div>
      <pre id="historyText">No commands sent yet.</pre>
 </div>
 <div id="altitudeBox">
    <div class="altitudeTitle">Altitude Monitor</div>
    <div>Current Altitude: <span id="altitudeValue">0.00 m</span></div>
    <div class="altitudeBarBackground">
        <div id="altitudeBar"></div>
    </div>
 </div>

<div class="missionPlannerBox">
    <div class="missionTitle">Mission Planner</div>
    <p class="missionSubtext">Create a simulated waypoint mission before uploading or starting it.</p>

    <div class="missionInputs">
        <label>Latitude</label>
        <input id="missionLat" type="number" step="0.0001" value="38.8895">

        <label>Longitude</label>
        <input id="missionLon" type="number" step="0.0001" value="-77.0353">

        <label>Altitude (m)</label>
        <input id="missionAlt" type="number" step="1" value="20">
    </div>

    <div class="missionButtons">
        <button class="button primary" onclick="addWaypoint()">Add Waypoint</button>
        <button class="button primary" onclick="uploadMission()">Upload Mission</button>
        <button class="button primary" onclick="startMission()">Start Mission</button>
        <button class="button danger" onclick="clearMission()">Clear Mission</button>
    </div>

    <div class="missionInfoGrid">
        <div>
            <strong>Mission Status</strong>
            <pre id="missionStatusBox">No mission loaded</pre>
        </div>
        <div>
            <strong>Waypoint List</strong>
            <pre id="waypointListBox">[]</pre>
        </div>
    </div>
</div>
        <script>
            let commandHistory = [];

	    let currentMode = "Multirotor";

             function setMode(mode) {
    currentMode = mode;

    document.getElementById('modeMultirotor').classList.remove('active');
    document.getElementById('modeFixedWing').classList.remove('active');
    document.getElementById('modeVTOL').classList.remove('active');

    if (mode === "Multirotor") {
        document.getElementById('btnArm').textContent = "Arm Drone";
        document.getElementById('btnLaunch').textContent = "Launch Drone";
        document.getElementById('btnMove').textContent = "Move Forward";
        document.getElementById('btnLand').textContent = "Land Drone";
        document.getElementById('btnStop').textContent = "Hold Position";

        document.getElementById('modeMultirotor').classList.add('active');
        document.getElementById('modeDescription').innerHTML =
            "Selected Mode: Multirotor<br>Control Profile: Vertical takeoff and landing drone";
    }

    if (mode === "Fixed-Wing") {
        document.getElementById('btnArm').textContent = "Arm System";
        document.getElementById('btnLaunch').textContent = "Launch Sequence";
        document.getElementById('btnMove').textContent = "Start Mission";
        document.getElementById('btnLand').textContent = "Return to Base";
        document.getElementById('btnStop').textContent = "Loiter Area";

        document.getElementById('modeFixedWing').classList.add('active');
        document.getElementById('modeDescription').innerHTML =
            "Selected Mode: Fixed-Wing<br>Control Profile: Launch, loiter, return-to-base, and mission flight";
    }

    if (mode === "VTOL") {
        document.getElementById('btnArm').textContent = "Arm System";
        document.getElementById('btnLaunch').textContent = "Vertical Takeoff";
        document.getElementById('btnMove').textContent = "Transition Flight";
        document.getElementById('btnLand').textContent = "Vertical Landing";
        document.getElementById('btnStop').textContent = "Mission Hold";

        document.getElementById('modeVTOL').classList.add('active');
        document.getElementById('modeDescription').innerHTML =
            "Selected Mode: VTOL<br>Control Profile: Vertical takeoff, transition, mission flight, and vertical landing";
    }

    document.getElementById('logText').textContent =
        "Platform mode selected: " + mode;
}
       async function sendCommand(endpoint) {
                try {
                    const response = await fetch(endpoint);
                    const data = await response.json();
                    console.log(data);
document.getElementById('logText').textContent =
    "Last command sent: " + endpoint;
const time = new Date().toLocaleTimeString();
commandHistory.unshift(time + " - " + endpoint);

if (commandHistory.length > 5) {
    commandHistory.pop();
}

document.getElementById('historyText').textContent = commandHistory.join("\\n");
                    updateStatus();
                } catch (error) {
                    console.error("Command error:", error);
                }
            }

            async function updateStatus() {
                try {
                    const response = await fetch('/status');
                    const data = await response.json();
document.getElementById('px4Status').textContent =
    data.connected ? "Connected" : "Disconnected";

document.getElementById('px4Status').style.color =
    data.connected ? "#22c55e" : "#ef4444";

document.getElementById('flightStatus').textContent =
    data.in_air ? "Flying" : "Ready";

document.getElementById('flightStatus').style.color =
    data.in_air ? "#38bdf8" : "#22c55e";
let altitude = data.altitude || 0;
let altitudePercent = Math.min(Math.max((altitude / 5) * 100, 0), 100);

document.getElementById('altitudeValue').textContent =
    altitude.toFixed(2) + " m";

document.getElementById('altitudeBar').style.width =
    altitudePercent + "%";
                    document.getElementById('statusText').textContent =
                        JSON.stringify(data, null, 2);
                } catch (error) {
                    document.getElementById('statusText').textContent =
                        "Status error: " + error;
                }
            }

            setInterval(updateStatus, 1000);
            updateStatus();
async function addWaypoint() {
    const lat = document.getElementById("missionLat").value;
    const lon = document.getElementById("missionLon").value;
    const alt = document.getElementById("missionAlt").value;

    const response = await fetch(`/add_waypoint?latitude=${lat}&longitude=${lon}&altitude=${alt}`, {
        method: "POST"
    });

    const data = await response.json();
    document.getElementById("missionStatusBox").innerText = data.status;
    refreshMissionStatus();
}

async function uploadMission() {
    const response = await fetch("/upload_mission", {
        method: "POST"
    });

    const data = await response.json();
    document.getElementById("missionStatusBox").innerText = data.message || data.status;
    refreshMissionStatus();
}

async function startMission() {
    const response = await fetch("/start_mission", {
        method: "POST"
    });

    const data = await response.json();
    document.getElementById("missionStatusBox").innerText = data.message || data.status;
    refreshMissionStatus();
}

async function clearMission() {
    const response = await fetch("/clear_mission", {
        method: "POST"
    });

    const data = await response.json();
    document.getElementById("missionStatusBox").innerText = data.status;
    refreshMissionStatus();
}

async function refreshMissionStatus() {
    const response = await fetch("/mission_status");
    const data = await response.json();

    document.getElementById("missionStatusBox").innerText = data.mission_state.message;
    document.getElementById("waypointListBox").innerText = JSON.stringify(data.waypoints, null, 2);
}

setInterval(refreshMissionStatus, 2000);
refreshMissionStatus();

        </script>
    </body>
    </html>
    """


@app.get("/swarm_dashboard", response_class=HTMLResponse)
async def swarm_dashboard():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>SSS AI Swarm Drone Software</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #111827;
            color: white;
            margin: 0;
            padding: 20px;
        }

        h1 {
            color: #38bdf8;
            margin-bottom: 5px;
        }

        .subtitle {
            color: #cbd5e1;
            margin-bottom: 25px;
        }

        .panel {
            background-color: #1f2937;
            border: 1px solid #374151;
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 20px;
        }

        .button {
            background-color: #2563eb;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 14px;
            margin: 5px;
            cursor: pointer;
            font-weight: bold;
        }

        .button:hover {
            background-color: #1d4ed8;
        }

        .danger {
            background-color: #dc2626;
        }

        .danger:hover {
            background-color: #991b1b;
        }

        .safe {
            background-color: #16a34a;
        }

        .safe:hover {
            background-color: #15803d;
        }

        select {
            padding: 10px;
            border-radius: 8px;
            margin-right: 8px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }

        th, td {
            border: 1px solid #374151;
            padding: 10px;
            text-align: center;
        }

        th {
            background-color: #0f172a;
            color: #38bdf8;
        }

        .status-box {
            background-color: #0f172a;
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 12px;
            color: #e5e7eb;
        }

        .selected {
            color: #22c55e;
            font-weight: bold;
        }

        .not-selected {
            color: #f87171;
        }
    </style>
</head>
<body>
    <h1>SSS AI Swarm Drone Software</h1>
    <div class="subtitle">Version 3 — Swarm Control Foundation | Simulation Mode</div>

    <div class="panel">
        <h2>Swarm Mission Status</h2>
        <div class="status-box" id="swarmMessage">Loading swarm status...</div>
    </div>

    <div class="panel">
        <h2>Swarm Control Actions</h2>

        <select id="droneSelect">
            <option value="1">SSS-DRONE-01 | MAV_SYS_ID 1</option>
            <option value="2">SSS-DRONE-02 | MAV_SYS_ID 2</option>
            <option value="3">SSS-DRONE-03 | MAV_SYS_ID 3</option>
            <option value="4">SSS-DRONE-04 | MAV_SYS_ID 4</option>
            <option value="5">SSS-DRONE-05 | MAV_SYS_ID 5</option>
        </select>

        <button class="button" onclick="selectDrone()">Select Drone</button>
        <button class="button" onclick="selectAllDrones()">Select All</button>
        <button class="button" onclick="clearSelection()">Clear Selection</button>
        <br><br>

        <button class="button danger" onclick="emergencyLandSelected()">Emergency Land Selected</button>
        <button class="button danger" onclick="emergencyLandAll()">Emergency Land All</button>
        <br><br>

        <button class="button safe" onclick="staggeredTakeoffSim()">Staggered Takeoff Simulation</button>
        <button class="button safe" onclick="formationHoldSim()">Formation Hold Simulation</button>
    </div>

    <div class="panel">
        <h2>Fleet Panel</h2>
        <table>
            <thead>
                <tr>
                    <th>Drone ID</th>
                    <th>MAV_SYS_ID</th>
                    <th>Connected</th>
                    <th>Armed</th>
                    <th>In Air</th>
                    <th>Altitude</th>
                    <th>Battery</th>
                    <th>Mission State</th>
                    <th>Formation</th>
                    <th>Selected</th>
                </tr>
            </thead>
            <tbody id="fleetTable">
                <tr>
                    <td colspan="10">Loading fleet data...</td>
                </tr>
            </tbody>
        </table>
    </div>

<script>
async function refreshSwarmStatus() {
    const response = await fetch("/swarm_status");
    const data = await response.json();

    document.getElementById("swarmMessage").innerText =
        data.swarm_status.message +
        " | Mode: " + data.swarm_status.mode +
        " | Total Drones: " + data.swarm_status.total_drones +
        " | Selected: " + JSON.stringify(data.swarm_status.selected_drones);

    const fleetTable = document.getElementById("fleetTable");
    fleetTable.innerHTML = "";

    data.fleet.forEach(drone => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${drone.drone_id}</td>
            <td>${drone.mav_sys_id}</td>
            <td>${drone.connected}</td>
            <td>${drone.armed}</td>
            <td>${drone.in_air}</td>
            <td>${drone.altitude}</td>
            <td>${drone.battery}</td>
            <td>${drone.mission_state}</td>
            <td>${drone.formation}</td>
            <td class="${drone.selected ? "selected" : "not-selected"}">${drone.selected}</td>
        `;

        fleetTable.appendChild(row);
    });
}

async function selectDrone() {
    const droneNumber = document.getElementById("droneSelect").value;
    await fetch(`/select_drone?drone_number=${droneNumber}`, { method: "POST" });
    refreshSwarmStatus();
}

async function selectAllDrones() {
    await fetch("/select_all_drones", { method: "POST" });
    refreshSwarmStatus();
}

async function clearSelection() {
    await fetch("/clear_selection", { method: "POST" });
    refreshSwarmStatus();
}

async function emergencyLandSelected() {
    await fetch("/emergency_land_selected", { method: "POST" });
    refreshSwarmStatus();
}

async function emergencyLandAll() {
    await fetch("/emergency_land_all", { method: "POST" });
    refreshSwarmStatus();
}

async function staggeredTakeoffSim() {
    await fetch("/staggered_takeoff_sim", { method: "POST" });
    refreshSwarmStatus();
}

async function formationHoldSim() {
    await fetch("/formation_hold_sim", { method: "POST" });
    refreshSwarmStatus();
}

setInterval(refreshSwarmStatus, 2000);
refreshSwarmStatus();
</script>

</body>
</html>
"""
