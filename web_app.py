import asyncio
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from mavsdk import System
from mavsdk.offboard import VelocityBodyYawspeed

app = FastAPI()
drone = System()
telemetry_data = {
    "connected": False,
    "armed": False,
    "in_air": False,
    "altitude": 0
}

@app.on_event("startup")
async def startup():
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
        </script>
    </body>
    </html>
    """
