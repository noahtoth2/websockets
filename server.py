# server.py
import asyncio
import websockets
import random
import uuid

# Estado del juego
# Se agrega "attempts" para contar intentos por jugador
game_state = {
    "number": random.randint(1, 100),
    "players": {},   # player_id -> {"name": str, "score": int, "attempts": int}
    "guesses": []    # historial de (name, guess, result)
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
        # Reiniciar ronda
        game_state["number"] = random.randint(1, 100)
        return f"🎉 ¡Correcto, {name}! Empieza nueva ronda."

# Genera un resumen de jugadores activos y sus intentos (solo consola)
def server_status():
    status = "Jugadores activos:\n"
    for pdata in game_state["players"].values():
        status += f" - {pdata['name']}: {pdata['attempts']} intentos\n"
    return status

async def handler(websocket):
    # Registrar nuevo jugador
    player_id = str(uuid.uuid4())
    await websocket.send("Bienvenido! Ingresa tu nombre:")
    name = await websocket.recv()

    # Inicializa datos del jugador
    game_state["players"][player_id] = {"name": name, "score": 0, "attempts": 0}
    clients[websocket] = player_id

    print(f"[Servidor] Nuevo jugador: {name}")
    print(f"[Servidor]\n{server_status()}")

    await websocket.send(f"¡Hola {name}! Adivina un número entre 1 y 100.")

    try:
        async for message in websocket:
            feedback = process_guess(player_id, message)

            # Mostrar en consola del servidor
            player_name = game_state['players'][player_id]['name']
            print(f"[Servidor] {player_name} adivinó {message}: {feedback}")
            print(f"[Servidor]\n{server_status()}")

            # Difundir solo feedback a todos los clientes
            for ws in clients:
                await ws.send(f"{player_name} adivinó {message}: {feedback}")
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        # Al desconectar, limpiar y notificar en consola
        disconnected_name = game_state["players"][player_id]["name"]
        del game_state["players"][player_id]
        del clients[websocket]
        print(f"[Servidor] Jugador desconectado: {disconnected_name}")
        print(f"[Servidor]\n{server_status()}")

async def main():
    async with websockets.serve(handler, "localhost", 6789):
        print("Servidor WebSocket corriendo en ws://localhost:6789")
        print(f"[Servidor]\n{server_status()}")
        await asyncio.Future()  # corre indefinidamente

if __name__ == "__main__":
    asyncio.run(main())