import uuid
import time
import hashlib
import hmac
import base64
import aiohttp
from setup import YOUR_SWITCHBOT_TOKEN, YOUR_SWITCHBOT_CLIENT_SECRET

TOKEN = YOUR_SWITCHBOT_TOKEN
SECRET = YOUR_SWITCHBOT_CLIENT_SECRET

def create_header(token: str, secret: str) -> dict:
    start = time.time()
    """
    Create authorization headers for the API request.
    
    Args:
        token (str): The API token.
        secret (str): The API secret.
    
    Returns:
        dict: The headers including the authorization signature.
    """
    nonce = uuid.uuid4()
    timestamp = int(round(time.time() * 1000))
    string_to_sign = f'{token}{timestamp}{nonce}'
    signature = base64.b64encode(hmac.new(secret.encode(), msg=string_to_sign.encode(), digestmod=hashlib.sha256).digest()).decode()
    end = time.time()
    print(f"create header time: {end - start} seconds")
    return {
        'Authorization': token,
        'Content-Type': 'application/json',
        'charset': 'utf8',
        't': str(timestamp),
        'sign': signature,
        'nonce': str(nonce)
    }

class CloudControl:
    def __init__(self, device_id: str ):
        """
        Initialize the CloudControl with the device ID and authorization headers.
        
        Args:
            device_id (str): The ID of the device to control.
        """
        self.header = create_header(TOKEN, SECRET)
        self.device_id = device_id

    async def send_command(self, session: aiohttp.ClientSession, command: str) -> dict:
        """
        Send a command to the device.
        
        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for the request.
            command (str): The command to send to the device.
        
        Returns:
            dict: The response from the API.
        """
        if not self.device_id:
            raise ValueError("Device ID not available!")

        url = f'https://api.switch-bot.com/v1.1/devices/{self.device_id}/commands'
        payload = {
            'command': command,
            'parameter': 'default',
            'commandType': 'command'
        }
        start_time = time.time()
        async with session.post(url, headers=self.header, json=payload) as response:
            end_time = time.time()
            print(f"{command} command execution time: {end_time - start_time} seconds")
            response_data = await response.json()
            if response.status == 200:
                return response_data
            else:
                response.raise_for_status()

    async def turn_on(self, session) -> dict:
        """Turn on the device."""
        return await self.send_command(session, 'turnOn')

    async def turn_off(self, session) -> dict:
        """Turn off the device."""
        return await self.send_command(session, 'turnOff')
    