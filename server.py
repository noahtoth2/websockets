# server.py
import asyncio
import websockets
import random
import uuid

# Configuración
MAX_PLAYERS = 50
PING_INTERVAL = 20
PING_TIMEOUT = 20
MAX_MESSAGE_SIZE = 1024
COUNTDOWN = 10  # segundos para nueva ronda

# Estado del juego: número secreto y datos de jugadores
game_state = {
    "number": random.randint(1, 100),
    "players": {}
}
clients = {}  # websocket -> player_id
state_lock = asyncio.Lock()

# Envío de mensaje a todos los clientes
async def broadcast(msg):
    to_remove = []
    for ws in clients:
        try:
            await ws.send(msg)
        except websockets.exceptions.ConnectionClosed:
            to_remove.append(ws)
    for ws in to_remove:
        await unregister(ws)

# Cuenta regresiva para nueva ronda
def format_countdown(sec):
    return f"🔄 Nueva ronda en {sec}..."

async def countdown_and_reset():
    # Realiza la cuenta regresiva visible para los clientes
    for sec in range(COUNTDOWN, 0, -1):
        await broadcast(format_countdown(sec))
        await asyncio.sleep(1)
    # Una vez termina, reiniciar el número secreto y avisar
    async with state_lock:
        game_state["number"] = random.randint(1, 100)
    await broadcast("🚀 ¡Nueva ronda iniciada! Adivina el nuevo número.")

# Procesa el intento de adivinar, devuelve (feedback, es_correcto)
async def process_guess(player_id, guess):
    async with state_lock:
        secret = game_state["number"]
        player = game_state["players"][player_id]
        player["attempts"] += 1

    try:
        val = int(guess)
    except ValueError:
        return "¡Por favor ingresa un número válido!", False

    if val < secret:
        return "Muy bajo!", False
    elif val > secret:
        return "Muy alto!", False
    else:
        async with state_lock:
            player["score"] += 1
            winner = player["name"]
        return f"🎉 ¡Correcto, {winner}!", True

# Registro y limpieza de conexiones
async def register(ws):
    if len(clients) >= MAX_PLAYERS:
        await ws.send("Servidor lleno, inténtalo más tarde.")
        await ws.close()
        raise asyncio.CancelledError()

async def unregister(ws):
    pid = clients.pop(ws, None)
    if pid:
        async with state_lock:
            game_state["players"].pop(pid, None)
        print(f"[Servidor] Desconectado: jugador {pid}")

# Impresión del estado en servidor
def print_server_status():
    print("[Servidor] Jugadores activos:")
    for pdata in game_state["players"].values():
        print(f" - {pdata['name']}: {pdata['attempts']} intentos, {pdata['score']} puntos")
    print()

async def handler(ws):
    await register(ws)
    await ws.send("Bienvenido! Ingresa tu nombre:")
    try:
        name = await asyncio.wait_for(ws.recv(), timeout=30)
    except asyncio.TimeoutError:
        await ws.close()
        return
    pid = str(uuid.uuid4())
    async with state_lock:
        game_state["players"][pid] = {"name": name, "score": 0, "attempts": 0}
        clients[ws] = pid
    print(f"[Servidor] Conectó: {name}")
    print_server_status()

    await ws.send(f"¡Hola {name}! Adivina un número entre 1 y 100.")

    try:
        async for message in ws:
            if len(message) > MAX_MESSAGE_SIZE:
                await ws.send("Mensaje demasiado largo.")
                continue
            feedback, correct = await process_guess(pid, message)
            # Enviar feedback al jugador
            await ws.send(feedback)
            print(f"[Servidor] {name} adivinó {message}: {feedback}")
            print_server_status()

            if correct:
                # Anunciar a todos el ganador y empezar cuenta regresiva
                await broadcast(f"🏆 {name} ha ganado esta ronda!")
                asyncio.create_task(countdown_and_reset())
    except (asyncio.CancelledError, websockets.exceptions.ConnectionClosed):
        pass
    finally:
        await unregister(ws)
        print(f"[Servidor] Desconectado: {name}")
        print_server_status()

async def main():
    server = await websockets.serve(
        handler,
        "0.0.0.0",
        6789,
        ping_interval=PING_INTERVAL,
        ping_timeout=PING_TIMEOUT
    )
    print("Servidor WebSocket corriendo en ws://0.0.0.0:6789")
    print_server_status()
    await server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[Servidor] Cerrando...")

# client.py (sin cambios en este ejemplo)
