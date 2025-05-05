import asyncio
from hbmqtt.client import MQTTClient
import subprocess

async def agent():
    client = MQTTClient()
    await client.connect('mqtt://localhost:1883/')
    await client.subscribe([("/commands", 0)])

    async def on_message():
        message = await client.deliver_message()
        packet = message.publish_packet
        command = packet.payload.data.decode()
        print(f"Executing command: {command}")
        try:
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            await client.publish('/response', output)
        except subprocess.CalledProcessError as e:
            await client.publish('/response', str(e.output))

    while True:
        await on_message()

loop = asyncio.get_event_loop()
loop.run_until_complete(agent())