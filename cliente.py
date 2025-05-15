import asyncio
import websockets

async def play():
    uri = "ws://<IP_DEL_SERVIDOR>:6789"  # Reemplaza con la IP o dominio del servidor
    try:
        async with websockets.connect(uri) as websocket:
            # Solicitar y enviar nombre
            greeting = await websocket.recv()
            print(greeting)
            name = input("Tu nombre: ").strip()
            while not name:
                name = input("⚠️ El nombre no puede estar vacío. Ingresa tu nombre: ").strip()
            await websocket.send(name)

            # Saludo inicial
            print(await websocket.recv())

            async def send_loop():
                while True:
                    guess = input("Tu intento: ").strip()
                    if not guess:
                        print("⚠️ Ingresa un número.")
                        continue
                    if not guess.isdigit():
                        print("⚠️ Solo se permiten números enteros.")
                        continue
                    await websocket.send(guess)

            async def recv_loop():
                try:
                    async for message in websocket:
                        print(f"{message}")
                except websockets.exceptions.ConnectionClosed:
                    print("🚫 Conexión cerrada.")

            await asyncio.gather(send_loop(), recv_loop())

    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    asyncio.run(play())