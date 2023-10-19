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
linhas = 24
colunas = 48


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

                mapa[state["digdug"][0]][state["digdug"][1]] = 0

                possible_movimentos = param_algoritmo(state, state["enemies"])

                nearest_enemy = nearest_distance(state, mapa)
                if nearest_enemy is None:
                    continue

                acao = algoritmo_search(
                    possible_movimentos, state, nearest_enemy, "greedy", mapa
                )

                if acao != None and len(acao) > 1:
                    nextStepList = acao[1][1:-1].split(", ")
                    nextStep = [int(nextStepList[0]), int(nextStepList[1])]

                    digdug_x, digdug_y = state["digdug"]
                    enemy_x, enemy_y = state["enemies"][nearest_enemy]["pos"]
                    enemy_dir = state["enemies"][nearest_enemy]["dir"]
                    next_x, next_y = nextStep[0], nextStep[1]

                    if avoid_Fyger(state, next_x, next_y, mapa):
                        continue

                    # Problema aqui
                    if (
                        abs(digdug_x - enemy_x) <= 2 and abs(digdug_y - enemy_y) == 0
                    ) or (
                        abs(digdug_y - enemy_y) <= 2 and abs(digdug_x - enemy_x) == 0
                    ):
                        await websocket.send(json.dumps({"cmd": "key", "key": "A"}))
                        continue
                    # Problema aqui
                    elif abs(digdug_x - enemy_x) == 0 and digdug_y < enemy_y:
                        await websocket.send(json.dumps({"cmd": "key", "key": "s"}))
                        continue
                    elif abs(digdug_x - enemy_x) == 0 and digdug_y > enemy_y:
                        await websocket.send(json.dumps({"cmd": "key", "key": "w"}))
                        continue
                    elif abs(digdug_y - enemy_y) == 0 and digdug_x < enemy_x:
                        await websocket.send(json.dumps({"cmd": "key", "key": "d"}))
                        continue
                    elif abs(digdug_y - enemy_y) == 0 and digdug_x > enemy_x:
                        await websocket.send(json.dumps({"cmd": "key", "key": "a"}))
                        continue
                    elif digdug_x < next_x:
                        await websocket.send(json.dumps({"cmd": "key", "key": "d"}))
                        continue
                    elif digdug_x > next_x:
                        await websocket.send(json.dumps({"cmd": "key", "key": "a"}))
                        continue
                    elif digdug_y < next_y:
                        await websocket.send(json.dumps({"cmd": "key", "key": "s"}))
                        continue
                    elif digdug_y > next_y:
                        await websocket.send(json.dumps({"cmd": "key", "key": "w"}))
                        continue
                else:
                    await websocket.send(json.dumps({"cmd": "key", "key": "A"}))
                    continue

            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return


def avoid_Fyger(state, next_x, next_y, mapa):
    for enemy in state["enemies"]:
        if enemy["name"] == "Fygar":
            enemy_x, enemy_y = enemy["pos"]
            dist_x = next_x - enemy_x
            dist_y = next_y - enemy_y
            if (
                (
                    (abs(dist_y) == 0)
                    and (dist_x >= -3)
                    and (dist_x <= 0)
                    and (enemy["dir"] == 3)
                )
                or (
                    (abs(dist_y) == 0)
                    and (dist_x <= 3)
                    and (dist_x >= 0)
                    and (enemy["dir"] == 1)
                )
                or (
                    (abs(dist_y) == 0)
                    and (enemy_x + 1 <= colunas - 1)
                    and (enemy_x - 1 >= 0)
                    and (
                        mapa[enemy_x + 1][enemy_y] == 1
                        or mapa[enemy_x - 1][enemy_y] == 1
                    )
                )
            ):
                return True

    return False


# TODO: Verificar se o inimigo esta a frente de uma pedra
def avoid_Rocks(state, next_x, next_y, mapa):
    pass


def algoritmo_search(movimentos, state, enemy, strategy, mapa):
    enemy_x, enemy_y = state["enemies"][enemy]["pos"]
    enemy_dir = state["enemies"][enemy]["dir"]
    # baixo - 2 ; direita - 1 ;esquerda - 3 ;cima - 0
    # ver se inimigo tem uma parede a frente
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
    if enemy_dir == 0 and enemy_y + 2 <= linhas - 1:  # cima
        enemy_y += 2
    elif enemy_dir == 1 and enemy_x - 2 >= 0:  # direita
        enemy_x -= 2
    elif enemy_dir == 2 and enemy_y - 2 >= 0:  # baixo
        enemy_y -= 2
    elif enemy_dir == 3 and enemy_x + 2 <= colunas - 1:  # esquerda
        enemy_x += 2

    p = SearchProblem(
        movimentos,
        str(tuple(state["digdug"])),
        str((enemy_x, enemy_y)),
    )
    t = SearchTree(p, strategy)

    return t.search()


def param_algoritmo(state, enemies):
    linhass = 48
    colunass = 24

    # Coordenads inimigos
    coordenadas_enemies = []
    for enemy in enemies:
        enemy_x, enemy_y = enemy["pos"]
        coordenadas_enemies.append([enemy_x, enemy_y])

    # Lista para armazenar os movimentos no formato ("(x_inicial, y_inicial)", "(x_final, y_final)", 1)
    possible_moves = []
    # Dicionario para armazenar as coordenadas no formato {"(x, y)": (x, y)}
    coordenadas = {}

    for linha in range(linhass):
        for coluna in range(colunass):
            # Adicionar movimentos para cima
            inicio = str((linha, coluna))
            if linha > 0:
                fim = str((linha - 1, coluna))
                fimList = [linha - 1, coluna]

                if fimList not in coordenadas_enemies:
                    possible_moves.append((inicio, fim, 1))
            # Adicionar movimentos para baixo
            if linha < linhass - 1:
                fim = str((linha + 1, coluna))
                fimList = [linha + 1, coluna]
                if fimList not in coordenadas_enemies:
                    possible_moves.append((inicio, fim, 1))
            # Adicionar movimentos para a esquerda
            if coluna > 0:
                fim = str((linha, coluna - 1))
                fimList = [linha, coluna - 1]
                if fimList not in coordenadas_enemies:
                    possible_moves.append((inicio, fim, 1))
            # Adicionar movimentos para a direita
            if coluna < colunass - 1:
                fim = str((linha, coluna + 1))
                fimList = [linha, coluna + 1]
                if fimList not in coordenadas_enemies:
                    possible_moves.append((inicio, fim, 1))

            coordenada = (linha, coluna)
            coordenada_str = f"({linha}, {coluna})"
            coordenadas[coordenada_str] = coordenada

    possible_movimentos = DigDug(
        possible_moves,
        coordenadas,
    )

    return possible_movimentos


def nearest_distance(state, mapa):
    nearest_distance = float("inf")
    nearest_enemy = None
    for i in range(len(state["enemies"])):
        enemy = state["enemies"][i]
        enemy_x, enemy_y = enemy["pos"]
        if mapa[enemy_x][enemy_y] == 1:
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
