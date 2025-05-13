# client.py
import asyncio
import websockets

async def play():
    uri = "ws://localhost:6789"
    async with websockets.connect(uri) as websocket:
        # Solicitud de nombre
        greeting = await websocket.recv()
        print(greeting)
        name = input("Tu nombre: ")
        await websocket.send(name)

        # Saludo inicial del servidor
        print(await websocket.recv())

        async def send_loop():
            while True:
                guess = input("Tu intento: ")
                await websocket.send(guess)

        async def recv_loop():
            async for message in websocket:
                # Mostrar solo feedback
                print(f"\n{message}")

        await asyncio.gather(send_loop(), recv_loop())

if __name__ == "__main__":
    asyncio.run(play())

# Instrucciones:
# 1. Instalar websockets: pip install websockets
# 2. Ejecutar servidor: python server.py
# 3. Ejecutar clientes: python client.py
# ¡Listo para la demo de la clase!