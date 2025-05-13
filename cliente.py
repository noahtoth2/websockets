# client.py
import asyncio
import websockets

async def play():
    uri = "ws://localhost:6789"
    async with websockets.connect(uri) as websocket:
        greeting = await websocket.recv()
        print(greeting)
        name = input("Tu nombre: ")
        await websocket.send(name)
        print(await websocket.recv())
        
        async def send_loop():
            while True:
                guess = input("Tu intento: ")
                await websocket.send(guess)
        
        async def recv_loop():
            async for message in websocket:
                print(f"\n{message}")
        
        await asyncio.gather(send_loop(), recv_loop())

if __name__ == "__main__":
    asyncio.run(play())