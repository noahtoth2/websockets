# server.py
import asyncio
import websockets
import random
import uuid
import signal

# Configuración
MAX_PLAYERS = 50
PING_INTERVAL = 20  # segundos
PING_TIMEOUT = 20   # segundos
MAX_MESSAGE_SIZE = 1024  # bytes máximo por mensaje

# Estado del juego: número secreto y datos de jugadores
game_state = {
    "number": random.randint(1, 100),
    "players": {}   # player_id -> {"name": str, "score": int, "attempts": int}
}
clients = {}  # websocket -> player_id
state_lock = asyncio.Lock()

# Procesa el intento de adivinar
async def process_guess(player_id, guess):
    async with state_lock:
        secret = game_state["number"]
        player = game_state["players"][player_id]
        player["attempts"] += 1

        try:
            val = int(guess)
        except ValueError:
            return "¡Por favor ingresa un número válido!"

        if val < secret:
            return "Muy bajo!"
        elif val > secret:
            return "Muy alto!"
        else:
            player["score"] += 1
            # Nueva ronda global
            game_state["number"] = random.randint(1, 100)
            # Broadcast de nueva ronda
            await broadcast_message("🔔 Nueva ronda: se escogió un nuevo número secreto.")
            return f"🎉 ¡Correcto, {player['name']}! Empieza nueva ronda."

# Envío de mensaje a todos los clientes
async def broadcast_message(msg):
    to_remove = []
    for ws in clients:
        try:
            await ws.send(msg)
        except websockets.exceptions.ConnectionClosed:
            to_remove.append(ws)
    # Limpiar clientes muertos
    for ws in to_remove:
        await unregister(ws)

# Registro y limpieza de conexiones
async def register(ws):
    if len(clients) >= MAX_PLAYERS:
        await ws.send("Servidor lleno, inténtalo más tarde.")
        await ws.close()
        raise asyncio.CancelledError()

async def unregister(ws):
    pid = clients.get(ws)
    if pid:
        async with state_lock:
            name = game_state['players'][pid]['name']
            del game_state['players'][pid]
            del clients[ws]
        print(f"[Servidor] Jugador desconectado: {name}")

# Handler principal
def print_server_status():
    print("[Servidor] Estado de jugadores activos:")
    for pdata in game_state["players"].values():
        print(f" - {pdata['name']}: {pdata['attempts']} intentos, {pdata['score']} puntos")
    print()

async def handler(ws):
    # Registrar conexión
    await register(ws)
    await ws.send("Bienvenido! Ingresa tu nombre:")
    name = await asyncio.wait_for(ws.recv(), timeout=30)

    pid = str(uuid.uuid4())
    async with state_lock:
        game_state["players"][pid] = {"name": name, "score": 0, "attempts": 0}
        clients[ws] = pid
    print(f"[Servidor] Nuevo jugador conectado: {name}")
    print_server_status()

    await ws.send(f"¡Hola {name}! Adivina un número entre 1 y 100.")
    try:
        async for message in ws:
            if len(message) > MAX_MESSAGE_SIZE:
                await ws.send("Mensaje demasiado largo.")
                continue
            feedback = await process_guess(pid, message)
            print(f"[Servidor] {name} adivinó {message}: {feedback}")
            print_server_status()
            await ws.send(feedback)
    except (asyncio.CancelledError, websockets.exceptions.ConnectionClosed):
        pass
    finally:
        await unregister(ws)

# Ciclo principal con señal de cierre
def shutdown(loop):
    for ws in list(clients.keys()):
        loop.create_task(ws.close())
    loop.stop()

async def main():
    # Inicia el servidor con ping para detectar desconexiones
    server = await websockets.serve(
        handler,
        "0.0.0.0",
        6789,
        ping_interval=PING_INTERVAL,
        ping_timeout=PING_TIMEOUT
    )
    print("Servidor WebSocket corriendo en ws://0.0.0.0:6789")
    print_server_status()
    try:
        await server.wait_closed()
    except KeyboardInterrupt:
        print("[Servidor] Cerrando servidor...")
        server.close()
        await server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[Servidor] Terminación forzada por usuario.")
