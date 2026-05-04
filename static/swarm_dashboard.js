async function refreshSwarmStatus() {
    const response = await fetch("/swarm_status");
    const data = await response.json();

    document.getElementById("swarmMessage").innerText =
        data.swarm_status.message +
        " | Mode: " + data.swarm_status.mode +
        " | Total Drones: " + data.swarm_status.total_drones +
        " | Selected: " + JSON.stringify(data.swarm_status.selected_drones);

const health = data.health_summary;

document.getElementById("swarmHealthSummary").innerText =
    "Total: " + health.total_drones +
    " | Leaders: " + health.leader_count +
    " | Followers: " + health.follower_count +
    " | Reserves: " + health.reserve_count +
    " | Selected: " + health.selected_count +
    " | In Air: " + health.in_air_count +
    " | Connected: " + health.connected_count +
    " | Simulation Only: " + health.simulation_only;
    const fleetTable = document.getElementById("fleetTable");
    fleetTable.innerHTML = "";
    const droneSelect = document.getElementById("droneSelect");
    const currentSelectedValue = droneSelect.value;
    droneSelect.innerHTML = "";

    data.fleet.forEach(drone => {
        const option = document.createElement("option");
        option.value = drone.nav_sys_id;
        option.textContent = `${drone.drone_id} | MAV_SYS_ID ${drone.nav_sys_id} | Role: ${drone.role}`;
        droneSelect.appendChild(option);
    });

    if (currentSelectedValue) {
        droneSelect.value = currentSelectedValue;
    }

    data.fleet.forEach(drone => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${drone.drone_id}</td>
            <td>${drone.nav_sys_id}</td>
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

async function addDrone() {
    const role = document.getElementById("roleSelect").value;
    await fetch(`/add_drone?role=${role}`, { method: "POST" });
    refreshSwarmStatus();
}

async function removeSelectedDrone() {
    const droneNumber = document.getElementById("droneSelect").value;

    if (!droneNumber) {
        alert("Please select a drone to remove.");
        return;
    }

    await fetch(`/remove_drone?drone_number=${droneNumber}`, { method: "POST" });
    refreshSwarmStatus();
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
