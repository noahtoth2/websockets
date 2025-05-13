# client.py
import asyncio
import websockets

async def play():
    uri = "ws://25.54.14.132:6789"  # Reemplaza con la IP o dominio del servidor
    async with websockets.connect(uri) as websocket:
        print(await websocket.recv())  # Solicita nombre
        name = input("Tu nombre: ")
        await websocket.send(name)
        print(await websocket.recv())  # Saludo inicial

        while True:
            guess = input("Tu intento: ")
            await websocket.send(guess)
            feedback = await websocket.recv()
            print(feedback)

if __name__ == "__main__":
    asyncio.run(play())

# Instrucciones:
# 1. Instalar websockets: pip install websockets
# 2. Ejecutar servidor: python server.py
# 3. Ejecutar clientes: python client.py
# ¡Listo para la demo!
