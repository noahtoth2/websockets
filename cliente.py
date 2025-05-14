
# client.py (versión mejorada con manejo de errores)
import asyncio
import websockets

async def play():
    uri = "ws://127.0.0.1:6789"  # Reemplaza con la IP o dominio del servidor
    try:
        async with websockets.connect(uri) as websocket:
            # Solicitar y enviar nombre
            initial = await websocket.recv()
            print(initial)
            name = input("Tu nombre: ").strip()
            while not name:
                name = input("⚠️ El nombre no puede estar vacío. Ingresa tu nombre: ").strip()
            await websocket.send(name)

            # Saludo inicial
            print(await websocket.recv())

            while True:
                guess = input("Tu intento: ").strip()

                # Validaciones locales
                if not guess:
                    print("⚠️ Ingresa un número.")
                    continue
                if not guess.isdigit():
                    print("⚠️ Solo se permiten números enteros.")
                    continue

                try:
                    await websocket.send(guess)
                    feedback = await websocket.recv()
                    print(feedback)
                except websockets.exceptions.ConnectionClosed:
                    print("🚫 Conexión cerrada por el servidor.")
                    break

    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    asyncio.run(play())

# Instrucciones:
# 1. Instalar websockets: pip install websockets
# 2. Ejecutar servidor: python server.py
# 3. Ejecutar clientes: python client.py
# ¡Listo para la demo mejorada!
