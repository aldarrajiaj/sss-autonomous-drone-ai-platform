import asyncio
from mavsdk import System

async def run():
	drone = System()
	await drone.connect(system_address="udpin://0.0.0.0:14540")

	print("waiting for drone to connect...")
	async for state in drone.core.connection_state():
		if state.is_connected:
			print("drone connected!")
			break

if __name__ == "__main__":
	asyncio.run(run())

