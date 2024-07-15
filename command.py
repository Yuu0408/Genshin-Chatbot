from cloud_api import CloudControl
import aiohttp
import time
from helper import get_device_id

async def execute(device, task):
    start_time = time.time()
    DEVICE_TYPE = device
    DEVICE_ID = get_device_id(DEVICE_TYPE)
    controller = CloudControl(DEVICE_ID)
    end_time = time.time()
    print(f"initialization: {end_time - start_time} seconds")
    
    async with aiohttp.ClientSession() as session:
      if controller.device_id:
        if task == "turn on":
            print("Turning on the device...")
            on_response = await controller.turn_on(session)
            print(f"Turn on response: {on_response}")
        elif task == "turn off":
            print("Turning off the device...")
            off_response = await controller.turn_off(session)
            print(f"Turn off response: {off_response}")

      else:
            print("Failed to initialize the device controller.")