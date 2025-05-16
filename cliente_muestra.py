# client.py

import asyncio
import websockets

async def run_client():
    """
    1) Abre conexión con el servidor
    2) Envía varios mensajes
    3) Escucha respuestas (eco o broadcast)
    4) Cierra conexión al finalizar
    """
    uri = "ws://localhost:8765"

    # 1. Realizamos el handshake automatic
    async with websockets.connect(uri) as websocket:
        print(f"Conectado a {uri}")

        # 2. Enviamos 3 mensajes de ejemplo
        for i in range(1, 4):
            msg = f"Mensaje #{i}"
            print(f"> Enviando: {msg}")
            await websocket.send(msg)

            # 3. Esperamos y mostramos la respuesta
            respuesta = await websocket.recv()
            print(f"< Recibido: {respuesta}")

        # 4. Al salir del 'with', la conexión se cierra automáticamente
        print("Cerrando conexión...")

if __name__ == "__main__":
    # Ejecutamos el cliente en el loop de asyncio
    asyncio.run(run_client())
