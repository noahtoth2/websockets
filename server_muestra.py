# server.py

import asyncio
import websockets

# ► 1. Lista global de conexiones activas
#    Nos permite hacer broadcast o enrutar mensajes.
connected_clients = set()

async def handler(websocket, path):
    """
    Cada vez que un cliente hace handshake y se conecta,
    ésta función se encarga de:
     1) Añadirlo a 'connected_clients'
     2) Recibir mensajes en bucle
     3) (Opcional) reenviar/broadcast a otros clientes
     4) Quitarlo al desconectarse
    """
    # 2. Registrar nueva conexión
    connected_clients.add(websocket)
    print(f"[+] Cliente conectado: {websocket.remote_address}")

    try:
        # 3. Bucle de recepción de mensajes
        async for message in websocket:
            print(f"   Recibido de {websocket.remote_address}: {message}")

            # 4. Ejemplo de broadcast: reenviar a todos excepto el emisor
            for client in connected_clients:
                if client is not websocket:
                    await client.send(f"[Broadcast] {message}")

    except websockets.exceptions.ConnectionClosed:
        # 5. Capturar desconexiones limpias o abruptas
        print(f"[-] Cliente desconectado: {websocket.remote_address}")

    finally:
        # 6. Limpiar la lista de conexiones
        connected_clients.remove(websocket)

async def main():
    """
    ▪ Crea el servidor WebSocket escuchando en localhost:8765
    ▪ El event loop de asyncio atenderá múltiples clientes
    """
    server = await websockets.serve(
        handler,        # Callback que acabamos de definir
        'localhost',    # Host
        8765            # Puerto
    )
    print("Servidor WebSocket escuchando en ws://localhost:8765")
    await server.wait_closed()

if __name__ == "__main__":
    # 7. Ejecutar el event loop principal
    asyncio.run(main())
