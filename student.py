import asyncio
import getpass
import json
import os
import time
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
        last_move = None

        while True:
            t1 = time.time()
            try:
                state = json.loads(await websocket.recv())

                if "map" in state:
                    mapa = state["map"]

                if "digdug" not in state or len(state["digdug"]) == 0:
                    continue

                if "enemies" not in state or len(state["enemies"]) == 0:
                    continue

                digdug_x, digdug_y = state["digdug"]

                mapa[digdug_x][digdug_y] = 0

                nearest_enemy = nearest_distance(state, mapa)
                if nearest_enemy is None:
                    continue

                # Too many enemies too close
                too_many_enemies = too_many_enemies_too_close(state, digdug_x, digdug_y)
                if too_many_enemies is not None:
                    nearest_enemy = too_many_enemies

                possible_movimentos = param_algoritmo(mapa)

                acao = algoritmo_search(
                    possible_movimentos, state, nearest_enemy, "greedy", mapa
                )

                t2 = time.time()
                print(f"Time: {t2 - t1}")

                if acao != None and len(acao) > 1:
                    nextStepList = acao[1][1:-1].split(", ")
                    nextStep = [int(nextStepList[0]), int(nextStepList[1])]
                    next_x, next_y = nextStep[0], nextStep[1]

                    enemy_x, enemy_y = state["enemies"][nearest_enemy]["pos"]
                    enemy_dir = state["enemies"][nearest_enemy]["dir"]

                    avoid_rock, move = avoid_Rocks(
                        state, next_x, next_y, digdug_x, digdug_y
                    )
                    if avoid_rock:
                        print("Avoiding rock")
                        await websocket.send(json.dumps({"cmd": "key", "key": move}))

                    # Avoid getting in front of fygar
                    if avoid_Fyger(state, next_x, next_y, mapa):
                        print("Avoiding fygar")
                        continue

                    if can_shoot(state, mapa, last_move, nearest_enemy):
                        await websocket.send(json.dumps({"cmd": "key", "key": "A"}))
                        last_move = "A"
                        continue
                    elif digdug_x < next_x:
                        await websocket.send(json.dumps({"cmd": "key", "key": "d"}))
                        last_move = "d"
                        continue
                    elif digdug_x > next_x:
                        await websocket.send(json.dumps({"cmd": "key", "key": "a"}))
                        last_move = "a"
                        continue
                    elif digdug_y < next_y:
                        await websocket.send(json.dumps({"cmd": "key", "key": "s"}))
                        last_move = "s"
                        continue
                    elif digdug_y > next_y:
                        await websocket.send(json.dumps({"cmd": "key", "key": "w"}))
                        last_move = "w"
                        continue
                else:
                    await websocket.send(json.dumps({"cmd": "key", "key": "A"}))
                    last_move = "A"
                    continue

            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return


def can_shoot(state, mapa, last_move, nearest_enemy):
    shooting_distance = 3
    digdug_x, digdug_y = state["digdug"]
    enemy_x, enemy_y = state["enemies"][nearest_enemy]["pos"]
    if last_move == "d":  # ultima jogada foi para a direita e o inimigo esta a direita
        if (
            enemy_x > digdug_x
            and enemy_y == digdug_y
            and enemy_x - digdug_x <= shooting_distance
            and mapa[enemy_x - 1][digdug_y] == 0
            and mapa[enemy_x - 2][digdug_y] == 0
            and mapa[enemy_x - 3][digdug_y] == 0
        ):
            return True
    elif (
        last_move == "a"
    ):  # ultima jogada foi para a esquerda e o inimigo esta a esquerda
        if (
            enemy_x < digdug_x
            and enemy_y == digdug_y
            and digdug_x - enemy_x <= shooting_distance
            and mapa[enemy_x + 1][digdug_y] == 0
            and mapa[enemy_x + 2][digdug_y] == 0
            and mapa[enemy_x + 3][digdug_y] == 0
        ):
            return True
    elif last_move == "w":  # ultima jogada foi para cima e o inimigo esta acima
        if (
            enemy_y < digdug_y
            and enemy_x == digdug_x
            and digdug_y - enemy_y <= shooting_distance
            and mapa[digdug_x][enemy_y + 1] == 0
            and mapa[digdug_x][enemy_y + 2] == 0
            and mapa[digdug_x][enemy_y + 3] == 0
        ):
            return True
    elif last_move == "s":  # ultima jogada foi para baixo e o inimigo esta abaixo
        if (
            enemy_y > digdug_y
            and enemy_x == digdug_x
            and enemy_y - digdug_y <= shooting_distance
            and mapa[digdug_x][enemy_y - 1] == 0
            and mapa[digdug_x][enemy_y - 2] == 0
            and mapa[digdug_x][enemy_y - 3] == 0
        ):
            return True
    elif last_move == "A":  # ultima jogada foi para atirar
        if (
            enemy_x > digdug_x
            and enemy_y == digdug_y
            and enemy_x - digdug_x <= shooting_distance
            and mapa[enemy_x - 1][digdug_y] == 0
            and mapa[enemy_x - 2][digdug_y] == 0
            and mapa[enemy_x - 3][digdug_y] == 0
        ):
            return True
        elif (
            enemy_x < digdug_x
            and enemy_y == digdug_y
            and digdug_x - enemy_x <= shooting_distance
            and mapa[enemy_x + 1][digdug_y] == 0
            and mapa[enemy_x + 2][digdug_y] == 0
            and mapa[enemy_x + 3][digdug_y] == 0
        ):
            return True
        elif (
            enemy_y < digdug_y
            and enemy_x == digdug_x
            and digdug_y - enemy_y <= shooting_distance
            and mapa[digdug_x][enemy_y + 1] == 0
            and mapa[digdug_x][enemy_y + 2] == 0
            and mapa[digdug_x][enemy_y + 3] == 0
        ):
            return True
        elif (
            enemy_y > digdug_y
            and enemy_x == digdug_x
            and enemy_y - digdug_y <= shooting_distance
            and mapa[digdug_x][enemy_y - 1] == 0
            and mapa[digdug_x][enemy_y - 2] == 0
            and mapa[digdug_x][enemy_y - 3] == 0
        ):
            return True
    return False


def avoid_Fyger(state, next_x, next_y, mapa):
    for enemy in state["enemies"]:
        if enemy["name"] == "Fygar":
            enemy_x, enemy_y = enemy["pos"]
            dist_x = next_x - enemy_x
            dist_y = next_y - enemy_y
            if abs(dist_y) != 0:
                return False
            if (
                ((0 >= dist_x >= -3) and (enemy["dir"] == 3))
                or ((0 <= dist_x <= 3) and (enemy["dir"] == 1))
                or (
                    (enemy_x + 1 <= colunas - 1)
                    and (enemy_x - 1 >= 0)
                    and (
                        mapa[enemy_x + 1][enemy_y] == 1
                        or mapa[enemy_x - 1][enemy_y] == 1
                    )
                )
            ):
                return True

    return False


def avoid_Rocks(state, next_x, next_y, digdug_x, digdug_y):
    move = None
    for rocks in state["rocks"]:
        rock_x, rock_y = rocks["pos"]
        if rock_x == next_x and rock_y == next_y:
            if rock_x == digdug_x + 1:  # se a rocha esta a direita do digdug
                return True, "w"
            elif rock_x == digdug_x - 1:  # se a rocha esta a esquerda do digdug
                return True, "s"
            elif rock_y == digdug_y + 1:  # se a rocha esta abaixo do digdug
                return True, "a"
            elif rock_y == digdug_y - 1:  # se a rocha esta acima do digdug
                return True, "d"
    return False, move


def calculate_distance(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)


def too_many_enemies_too_close(state, next_x, next_y):
    min_distance = float("inf")
    close_enemies = []

    for enemy in state["enemies"]:
        enemy_x, enemy_y = enemy["pos"]
        distance = calculate_distance(next_x, next_y, enemy_x, enemy_y)

        if distance < min_distance:
            min_distance = distance

        if distance <= 3:
            close_enemies.append(enemy)

    if len(close_enemies) >= 2:
        for enemy in state["enemies"]:
            if enemy not in close_enemies:
                return state["enemies"].index(enemy)
    return None


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
    elif enemy_dir == 0 and enemy_y + 2 <= linhas - 1:  # cima
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


def param_algoritmo(mapa):
    linhass = 48
    colunass = 24

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
                if mapa[linha - 1][coluna] == 0:
                    possible_moves.append((inicio, fim, 1))
                else:
                    possible_moves.append((inicio, fim, 100))
            # Adicionar movimentos para baixo
            if linha < linhass - 1:
                fim = str((linha + 1, coluna))
                if mapa[linha + 1][coluna] == 0:
                    possible_moves.append((inicio, fim, 1))
                else:
                    possible_moves.append((inicio, fim, 100))
            # Adicionar movimentos para a esquerda
            if coluna > 0:
                fim = str((linha, coluna - 1))
                if mapa[linha][coluna - 1] == 0:
                    possible_moves.append((inicio, fim, 1))
                else:
                    possible_moves.append((inicio, fim, 100))
            # Adicionar movimentos para a direita
            if coluna < colunass - 1:
                fim = str((linha, coluna + 1))
                if mapa[linha][coluna + 1] == 0:
                    possible_moves.append((inicio, fim, 1))
                else:
                    possible_moves.append((inicio, fim, 100))

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
