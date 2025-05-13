# server.py
import asyncio
import websockets
import random
import uuid

# Estado del juego
game_state = {
    "number": random.randint(1, 100),
    "players": {},   # player_id -> {"name": str, "score": int}
    "guesses": []    # historial de (name, guess, result)
}

clients = {}  # websocket -> player_id

def process_guess(player_id, guess):
    secret = game_state["number"]
    try:
        guess = int(guess)
    except ValueError:
        return "¡Por favor ingresa un número válido!"
    
    if guess < secret:
        result = "Muy bajo!"
    elif guess > secret:
        result = "Muy alto!"
    else:
        name = game_state["players"][player_id]["name"]
        game_state["players"][player_id]["score"] += 1
        result = f"🎉 ¡Correcto, {name}! Empieza nueva ronda."
        game_state["number"] = random.randint(1, 100)
    
    name = game_state["players"][player_id]["name"]
    game_state["guesses"].append((name, guess, result))
    return result

async def handler(websocket):
    # Registrar jugador
    player_id = str(uuid.uuid4())
    await websocket.send("Bienvenido! Ingresa tu nombre:")
    name = await websocket.recv()
    
    game_state["players"][player_id] = {"name": name, "score": 0}
    clients[websocket] = player_id
    await websocket.send(f"¡Hola {name}! Adivina un número entre 1 y 100.")
    
    try:
        async for message in websocket:
            feedback = process_guess(player_id, message)
            # Difundir a todos los clientes
            for ws in clients:
                await ws.send(f"{game_state['players'][player_id]['name']} adivinó {message}: {feedback}")
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        # Limpiar al desconectar
        del game_state["players"][player_id]
        del clients[websocket]

async def main():
    async with websockets.serve(handler, "localhost", 6789):
        print("Servidor WebSocket corriendo en ws://localhost:6789")
        await asyncio.Future()  # corre indefinidamente

if __name__ == "__main__":
    asyncio.run(main())
