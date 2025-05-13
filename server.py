# server.py
import asyncio
import websockets
import random
import uuid

# Estado del juego: número secreto y datos de jugadores
game_state = {
    "number": random.randint(1, 100),
    "players": {}   # player_id -> {"name": str, "score": int, "attempts": int}
}

clients = {}  # websocket -> player_id

# Procesa el intento de adivinar
def process_guess(player_id, guess):
    secret = game_state["number"]
    player = game_state["players"][player_id]
    player["attempts"] += 1

    try:
        guess = int(guess)
    except ValueError:
        return "¡Por favor ingresa un número válido!"

    if guess < secret:
        return "Muy bajo!"
    elif guess > secret:
        return "Muy alto!"
    else:
        name = player["name"]
        player["score"] += 1
        game_state["number"] = random.randint(1, 100)
        return f"🎉 ¡Correcto, {name}! Empieza nueva ronda."

# Muestra en consola del servidor el estado de jugadores
def print_server_status():
    print("[Servidor] Estado de jugadores activos:")
    for pdata in game_state["players"].values():
        print(f" - {pdata['name']}: {pdata['attempts']} intentos, {pdata['score']} puntos")
    print()

async def handler(websocket):
    # Registro de nuevo jugador
    await websocket.send("Bienvenido! Ingresa tu nombre:")
    name = await websocket.recv()
    player_id = str(uuid.uuid4())
    game_state["players"][player_id] = {"name": name, "score": 0, "attempts": 0}
    clients[websocket] = player_id

    # Log en servidor
    print(f"[Servidor] Nuevo jugador conectado: {name}")
    print_server_status()

    await websocket.send(f"¡Hola {name}! Adivina un número entre 1 y 100.")

    try:
        async for message in websocket:
            feedback = process_guess(player_id, message)
            player_name = game_state['players'][player_id]['name']

            # Log en servidor
            print(f"[Servidor] {player_name} adivinó {message}: {feedback}")
            print_server_status()

            # Solo enviar feedback al cliente que hizo el intento
            await websocket.send(feedback)

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        # Jugador desconectado
        name = game_state["players"][player_id]['name']
        del game_state["players"][player_id]
        del clients[websocket]
        print(f"[Servidor] Jugador desconectado: {name}")
        print_server_status()

async def main():
    # Escuchar todas las interfaces en el puerto 6789
    async with websockets.serve(handler, "0.0.0.0", 6789):
        print("Servidor WebSocket corriendo en ws://0.0.0.0:6789")
        print_server_status()
        await asyncio.Future()  # Ejecución indefinida

if __name__ == "__main__":
    asyncio.run(main())