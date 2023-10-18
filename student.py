import asyncio
import getpass
import json
import os
import websockets
from digdug import *
import math
from tree_search import *
from digdug import *

possible_movimentos = None
mapa = None


async def agent_loop(server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        while True:
            try:
                state = json.loads(await websocket.recv())

                if "map" in state:
                    mapa = state["map"]

                if "digdug" not in state or len(state["digdug"]) == 0:
                    continue

                if "enemies" not in state or len(state["enemies"]) == 0:
                    continue

                possible_movimentos = param_algoritmo(state, state["enemies"])

                mapa[state["digdug"][0]][state["digdug"][1]] = 0

                nearest_enemy = nearest_distance(state, mapa)
                if nearest_enemy is None:
                    continue

                acao = algoritmo_search(
                    possible_movimentos, state, nearest_enemy, "greedy", mapa
                )

                if acao != None and len(acao) > 1:
                    objectiveList = acao[1][1:-1].split(", ")
                    objective = [int(objectiveList[0]), int(objectiveList[1])]

                    digdug_x, digdug_y = state["digdug"]
                    next_x, next_y = objective[0], objective[1]

                    avoid_Fygers, move = avoid_Fyger(
                        state, next_x, next_y, mapa, digdug_x, digdug_y
                    )
                    if avoid_Fygers:
                        await websocket.send(json.dumps({"cmd": "key", "key": move}))

                    enemyx, enemyy = state["enemies"][nearest_enemy]["pos"]

                    if (
                        abs(digdug_x - enemyx) <= 2 and abs(digdug_y - enemyy) == 0
                    ) or (abs(digdug_y - enemyy) <= 2 and abs(digdug_x - enemyx) == 0):
                        await websocket.send(json.dumps({"cmd": "key", "key": "A"}))
                        continue

                    elif digdug_x < next_x:
                        await websocket.send(json.dumps({"cmd": "key", "key": "d"}))
                    elif digdug_x > next_x:
                        await websocket.send(json.dumps({"cmd": "key", "key": "a"}))
                    elif digdug_y < next_y:
                        await websocket.send(json.dumps({"cmd": "key", "key": "s"}))
                    elif digdug_y > next_y:
                        await websocket.send(json.dumps({"cmd": "key", "key": "w"}))
                else:
                    enemydir = state["enemies"][nearest_enemy]["dir"]

                    if enemydir == 0:
                        await websocket.send(json.dumps({"cmd": "key", "key": "w"}))
                    elif enemydir == 1:
                        await websocket.send(json.dumps({"cmd": "key", "key": "d"}))
                    elif enemydir == 2:
                        await websocket.send(json.dumps({"cmd": "key", "key": "s"}))
                    elif enemydir == 3:
                        await websocket.send(json.dumps({"cmd": "key", "key": "a"}))

            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return


def avoid_Fyger(state, next_x, next_y, mapa, digdug_x, digdug_y):
    for enemy in state["enemies"]:
        if enemy["name"] == "Fygar":
            enemy_x, enemy_y = enemy["pos"]
            if (
                (abs(next_y - enemy_y) == 0)
                and (next_x - enemy_x >= -4)
                and (enemy["dir"] == 3)
            ):
                if mapa[digdug_x][digdug_y + 1] != None:
                    move = "s"
                elif mapa[digdug_x][digdug_y - 1] != None:
                    move = "w"
                return True, move
                break
            elif (
                (abs(next_y - enemy_y) == 0)
                and (next_x - enemy_x <= 4)
                and (enemy["dir"] == 1)
            ):
                if digdug_y + 1 <= 23:
                    move = "s"
                elif digdug_y - 1 >= 0:
                    move = "w"
                return True, move
                break
    return False, None


def algoritmo_search(movimentos, state, enemy, strategy, mapa):
    enemy_x, enemy_y = state["enemies"][enemy]["pos"]
    print(enemy_x, enemy_y)
    enemydir = state["enemies"][enemy]["dir"]
    # baixo - 2 ; direita - 1 ;esquerda - 3 ;cima - 0
    # ver se inimigo tem uma parede a frente
    if (
        enemydir == 0
        and enemy_y + 3 <= 23
        and enemy_y - 1 >= 0
        and mapa[enemy_x][enemy_y - 1] == 1
    ):  # cima
        enemy_y += 3
    elif (
        enemydir == 1
        and enemy_x + 1 <= 47
        and enemy_x - 3 > 0
        and mapa[enemy_x + 1][enemy_y] == 1
    ):  # direita
        enemy_x -= 3
    elif (
        enemydir == 2
        and enemy_y - 3 > 0
        and enemy_y + 1 <= 23
        and mapa[enemy_x][enemy_y + 1] == 1
    ):  # baixo
        enemy_y -= 3
    elif (
        enemydir == 3
        and enemy_x + 3 <= 47
        and enemy_x - 1 >= 0
        and mapa[enemy_x - 1][enemy_y] == 1
    ):  # esquerda
        enemy_x += 3
    elif enemydir == 0 and enemy_y + 2 <= 23:  # cima
        enemy_y += 2
    elif enemydir == 1 and enemy_x - 2 >= 0:  # direita
        enemy_x -= 2
    elif enemydir == 2 and enemy_y - 2 >= 0:  # baixo
        enemy_y -= 2
    elif enemydir == 3 and enemy_x + 2 <= 47:  # esquerda
        enemy_x += 2

    p = SearchProblem(
        movimentos,
        str(tuple(state["digdug"])),
        str((enemy_x, enemy_y)),
    )
    t = SearchTree(p, strategy)

    print(t.search())
    return t.search()


def nearest_distance(state, mapa):
    nearest_distance = float("inf")
    nearest_enemy = None
    for i in range(len(state["enemies"])):
        enemy = state["enemies"][i]
        enemy_x, enemy_y = enemy["pos"]
        if mapa[enemy_x][enemy_y] == 1:
            continue

        distance = math.dist(state["digdug"], enemy["pos"])
        if distance + 10 < nearest_distance:
            nearest_distance = distance
            nearest_enemy = i

    return nearest_enemy


def param_algoritmo(state, enemies):
    # Tamanho da matriz
    linhas = 48
    colunas = 24

    # Lista para armazenar os movimentos no formato [(<inicio>, <fim>, 1)]
    possible_moves = []
    # Dicionario para armazenar as coordenadas no formato {"(x, y)": (x, y)}
    coordenadas = {}

    # Coordenads inimigos
    coordenadas_enemies = []
    for enemy in enemies:
        enemy_x, enemy_y = enemy["pos"]
        coordenadas_enemies.append([enemy_x, enemy_y])

    for linha in range(linhas):
        for coluna in range(colunas):
            # Adicionar movimentos para cima
            inicio = str((linha, coluna))
            if linha > 0:
                fim = str((linha - 1, coluna))

                if [linha - 1, coluna] not in coordenadas_enemies:
                    possible_moves.append((inicio, fim, 1))
            # Adicionar movimentos para baixo
            if linha < linhas - 1:
                fim = str((linha + 1, coluna))
                if [linha + 1, coluna] not in coordenadas_enemies:
                    possible_moves.append((inicio, fim, 1))
            # Adicionar movimentos para a esquerda
            if coluna > 0:
                fim = str((linha, coluna - 1))
                if [linha, coluna - 1] not in coordenadas_enemies:
                    possible_moves.append((inicio, fim, 1))
            # Adicionar movimentos para a direita
            if coluna < colunas - 1:
                fim = str((linha, coluna + 1))
                if [linha, coluna + 1] not in coordenadas_enemies:
                    possible_moves.append((inicio, fim, 1))

            coordenada = (linha, coluna)
            coordenada_str = f"({linha}, {coluna})"
            coordenadas[coordenada_str] = coordenada

    possible_movimentos = DigDug(
        # Ligacoes por estrada
        possible_moves,
        coordenadas,
    )

    return possible_movimentos


loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))
