import asyncio
import getpass
import json
import os
import websockets
import math
from search import *

mapa = None
linhas = 24
colunas = 48


async def agent_loop(server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))
        last_move = None
        i = True
        moves_fygar = {}
        while True:
            try:
                state = json.loads(await websocket.recv())
                if "map" in state:
                    mapa = state["map"]

                if "digdug" not in state or len(state["digdug"]) == 0:
                    continue

                if "enemies" not in state or len(state["enemies"]) == 0:
                    continue

                # Set rocks as 1 on the map (to be used in the A* algorithm)
                if i:
                    for rock in state["rocks"]:
                        rock_x, rock_y = rock["pos"]
                        mapa[rock_x][rock_y] = 1
                    i = False

                # Update player's position on the map
                digdug_x, digdug_y = state["digdug"]

                mapa[digdug_x][digdug_y] = 0  # Remove wall from the map

                # Update Fygar enemies' move history
                for enemy in state["enemies"]:
                    if enemy["name"] == "Fygar":
                        if enemy["id"] not in moves_fygar:
                            moves_fygar[enemy["id"]] = [enemy["pos"]]
                        else:
                            if moves_fygar[enemy["id"]][-1] != enemy["pos"]:
                                moves_fygar[enemy["id"]].append(enemy["pos"])

                # Get the index of the nearest enemy to the player
                nearest_enemy = nearest_distance(state)
                if nearest_enemy is None:
                    continue

                # Preform A* algorithm to find the best path to the nearest enemy, if possible
                acao = astar(
                    mapa,
                    (digdug_x, digdug_y),
                    state,
                    nearest_enemy,
                    last_move,
                    moves_fygar,
                )
                # If the A* algorithm fails, try again with the control flag set to True, runs away avoiding enemies
                if acao == None:
                    acao = astar(
                        mapa,
                        (digdug_x, digdug_y),
                        state,
                        nearest_enemy,
                        last_move,
                        moves_fygar,
                        controlo=True,
                    )

                if acao != None and len(acao) == 2 and acao[1] == acao[0]:
                    last_move = "A"
                    await websocket.send(json.dumps({"cmd": "key", "key": "A"}))
                    continue
                elif acao != None and len(acao) > 1:
                    nextStepList = acao[1]
                    nextStep = [int(nextStepList[0]), int(nextStepList[1])]

                    move = get_action((digdug_x, digdug_y), nextStep)
                    last_move = move
                    await websocket.send(json.dumps({"cmd": "key", "key": move}))
                    continue
                elif acao != None and len(acao) == 1 and acao == "A":
                    last_move = "A"
                    await websocket.send(json.dumps({"cmd": "key", "key": "A"}))
                    continue
            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return


def get_action(current, next):
    """
    Determines the action to move from the current position to the next position.

    This function takes two positions, the current and the next, and returns the action
    needed to move from the current position to the next position in the game.

    Args:
        current (tuple): A tuple representing the current coordinates (x, y).
        next (tuple): A tuple representing the target coordinates (x, y).

    Returns:
        str: The action ('a' for left, 'd' for right, 'w' for up, 's' for down) to move from
        the current position to the next position.
    """
    current_x, current_y = current
    next_x, next_y = next

    if current_x < next_x:
        return "d"
    elif current_x > next_x:
        return "a"
    elif current_y < next_y:
        return "s"
    elif current_y > next_y:
        return "w"


def nearest_distance(state):
    """
    Finds the index of the nearest enemy to the player in the game state.

    This function calculates the Euclidean distance between the player (digdug) and each enemy
    in the game state and returns the index of the enemy that is closest to the player.

    Args:
        state (dict): The game state containing information about the current game situation.

    Returns:
        int: The index of the nearest enemy in the "enemies" list of the game state.
    """
    nearest_distance = float("inf")
    nearest_enemy = None
    for i in range(len(state["enemies"])):
        enemy = state["enemies"][i]
        distance = math.dist(state["digdug"], enemy["pos"])
        if distance < nearest_distance:
            nearest_distance = distance
            nearest_enemy = i

    return nearest_enemy


loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))
