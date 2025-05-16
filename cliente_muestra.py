# client.py
import asyncio
import websockets

async def run():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as ws:
        print("[Cliente] Conectado a servidor")
        for i in range(3):
            mensaje = f"Hola {i+1}"
            print(f"[Cliente] → {mensaje}")
            await ws.send(mensaje)
            respuesta = await ws.recv()
            print(f"[Cliente] ← {respuesta}")

if __name__ == "__main__":
    asyncio.run(run())
