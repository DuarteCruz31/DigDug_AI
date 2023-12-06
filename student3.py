import asyncio
import getpass
import json
import os
import websockets
import math
from search3 import *

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

                nearest_enemy = nearest_distance(state, mapa)
                if nearest_enemy is None:
                    continue

                enemy_x, enemy_y = state["enemies"][nearest_enemy]["pos"]

                acao = algoritmo_search(state, nearest_enemy, mapa, last_move)

                if acao != None and len(acao) > 1:
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
                elif acao != None and len(acao) == 1 and len(acao[0]) == 1:
                    last_move = acao[0]
                    print(acao[0])
                    await websocket.send(json.dumps({"cmd": "key", "key": acao[0]}))
                    continue
                elif acao != None and len(acao) == 1:
                    copia_mapa = mapa.copy()
                    # No movement found, try to shoot
                    if enemy_y == digdug_y:
                        if enemy_x < digdug_x and enemy_x != digdug_x - 1:
                            copia_mapa[digdug_x - 1][digdug_y] = 0
                            direction = "a"
                        elif enemy_x > digdug_x and enemy_x != digdug_x + 1:
                            copia_mapa[digdug_x + 1][digdug_y] = 0
                            direction = "d"
                    elif enemy_x == digdug_x:
                        if enemy_y < digdug_y and enemy_y != digdug_y - 1:
                            copia_mapa[digdug_x][digdug_y - 1] = 0
                            direction = "w"
                        elif enemy_y > digdug_y and enemy_y != digdug_y + 1:
                            copia_mapa[digdug_x][digdug_y + 1] = 0
                            direction = "s"
                    else:
                        print("No movement or shoot found")

                    if can_shoot(
                        state, copia_mapa, direction, nearest_enemy, digdug_x, digdug_y
                    ):
                        print(direction)
                        await websocket.send(
                            json.dumps({"cmd": "key", "key": direction})
                        )
                        last_move = direction
                    else:
                        copia_mapa[digdug_x][digdug_y] = 1
                        print("No movement or shoot found")

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


def nearest_distance(state, mapa):
    nearest_distance = float("inf")
    nearest_enemy = None
    for i in range(len(state["enemies"])):
        enemy = state["enemies"][i]
        distance = math.dist(state["digdug"], enemy["pos"])
        if distance < nearest_distance:
            nearest_distance = distance
            nearest_enemy = i

    return nearest_enemy


def algoritmo_search(state, enemy, mapa, last_move):
    enemy_x, enemy_y = state["enemies"][enemy]["pos"]
    digdug_x, digdug_y = state["digdug"]
    enemy_name = state["enemies"][enemy]["name"]
    enemy_dir = state["enemies"][enemy]["dir"]

    if (
        enemy_dir == 0
        and enemy_y + 3 <= linhas - 1
        and enemy_y - 1 >= 0
        and mapa[enemy_x][enemy_y - 1] == 1
    ):  # cima
        enemy_y += 3
    elif (
        enemy_dir == 1
        and enemy_x - 3 > 0
        and enemy_x + 1 <= colunas - 1
        and mapa[enemy_x + 1][enemy_y] == 1
    ):  # direita
        enemy_x -= 3
    elif (
        enemy_dir == 2
        and enemy_y - 3 > 0
        and enemy_y + 1 <= linhas - 1
        and mapa[enemy_x][enemy_y + 1] == 1
    ):  # baixo
        enemy_y -= 3
    elif (
        enemy_dir == 3
        and enemy_x + 3 <= colunas - 1
        and enemy_x - 1 >= 0
        and mapa[enemy_x - 1][enemy_y] == 1
    ):  # esquerda
        enemy_x += 3
    else:
        if enemy_dir == 0 and enemy_y + 2 <= linhas - 1:  # cima
            enemy_y += 2
        elif enemy_dir == 1 and enemy_x - 2 >= 0:  # direita
            enemy_x -= 2
        elif enemy_dir == 2 and enemy_y - 2 >= 0:  # baixo
            enemy_y -= 2
        elif enemy_dir == 3 and enemy_x + 2 <= colunas - 1:  # esquerda
            enemy_x += 2

    return astar(
        mapa, (digdug_x, digdug_y), (enemy_x, enemy_y), state, enemy, last_move
    )


loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))
