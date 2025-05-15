# client.py (uso de run_in_executor para no bloquear el bucle)
import asyncio
import websockets

async def play():
    uri = "ws://25.54.14.132:6789"  # Reemplaza con tu IP o dominio

    try:
        async with websockets.connect(uri) as websocket:
            # Solicitar y enviar nombre (bloqueo inicial aceptable)
            greeting = await websocket.recv()
            print(greeting)
            name = input("Tu nombre: ").strip()
            while not name:
                name = input("⚠️ El nombre no puede estar vacío. Ingresa tu nombre: ").strip()
            await websocket.send(name)

            # Saludo inicial
            print(await websocket.recv())

            loop = asyncio.get_event_loop()

            async def send_loop():
                while True:
                    # input sin bloquear el event loop
                    guess = await loop.run_in_executor(None, input, "Tu intento: ")
                    guess = guess.strip()
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

            # Ejecutar en paralelo sin que input bloquee recv_loop
            await asyncio.gather(send_loop(), recv_loop())

    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    asyncio.run(play())