import asyncio
import getpass
import json
import os
import websockets
import math
from searchAndre import *

mapa = None
linhas = 24
colunas = 48


async def agent_loop(server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))
        last_move = None
        i = True
        while True:
            try:
                state = json.loads(await websocket.recv())
                if "map" in state:
                    mapa = state["map"]

                if "digdug" not in state or len(state["digdug"]) == 0:
                    continue

                if "enemies" not in state or len(state["enemies"]) == 0:
                    continue

                if i:
                    for rock in state["rocks"]:
                        rock_x, rock_y = rock["pos"]
                        mapa[rock_x][rock_y] = 1
                    i = False

                digdug_x, digdug_y = state["digdug"]

                mapa[digdug_x][digdug_y] = 0

                exist_pooka = False
                for enemy in state["enemies"]:
                    if enemy["name"] == "Pooka":
                        exist_pooka = True
                        break

                nearest_enemy = nearest_distance(state, exist_pooka)
                if nearest_enemy is None:
                    continue

                acao = astar(
                    mapa, (digdug_x, digdug_y), state, nearest_enemy, last_move
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


def nearest_distance(state, exist_pooka):
    nearest_distance = float("inf")
    nearest_enemy = None
    for i in range(len(state["enemies"])):
        enemy = state["enemies"][i]
        if enemy["name"] != "Pooka" and exist_pooka:
            continue
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
