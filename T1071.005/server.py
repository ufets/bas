import asyncio
from hbmqtt.client import MQTTClient

async def c2():
    client = MQTTClient()
    await client.connect('mqtt://localhost:1883/')
    await client.subscribe([("/response", 0)])

    async def get_message():
        message = await client.deliver_message()
        packet = message.publish_packet
        print(f"Response: {packet.payload.data.decode()}")

    while True:
        command = input("Enter command: ")
        await client.publish('/commands', command.encode())
        await get_message()

loop = asyncio.get_event_loop()
loop.run_until_complete(c2())