1
import asyncio
from mavsdk import System
from mavsdk.offboard import VelocityBodyYawspeed

async def run():
	drone = System()
	await drone.connect(system_address="udpin://0.0.0.0:14540")

	print("Waiting for drone to connect...")
	async for state in drone.core.connection_state():
		if state.is_connected:
			print("Drone connected!")
			break

	print("Arming...")
	await drone.action.arm()

	print("Taking off...")
	await drone.action.takeoff()
	await asyncio.sleep(5)

	await drone.offboard.set_velocity_body(
		VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0)
	)
	await drone.offboard.start()

	print("Moving forward...")
	for _ in range(40):
		await drone.offboard.set_velocity_body(
			VelocityBodyYawspeed(2.0, 0.0, 0.0, 0.0)
		)
		await asyncio.sleep(0.5)

	print("Stopping...")
	await drone.offboard.set_velocity_body(
		VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0)
	)

	await asyncio.sleep(5)


	print("Landing...")
	await drone.action.land()


if __name__ == "__main__":
	asyncio.run(run())
