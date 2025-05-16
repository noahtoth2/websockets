# server.py
import asyncio
import websockets

async def handler(websocket):
    print("[Servidor] Cliente conectado")
    try:
        async for msg in websocket:
            print(f"[Servidor] Recibido: {msg}")
            await websocket.send(f"ECO: {msg}")
    except websockets.ConnectionClosed:
        print("[Servidor] Cliente desconectado")

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("Servidor escuchando en ws://localhost:8765")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
