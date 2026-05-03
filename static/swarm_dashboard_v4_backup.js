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
