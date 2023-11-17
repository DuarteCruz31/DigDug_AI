import asyncio
import getpass
import json
import os
import websockets
import math
from search import *

possible_movimentos = None
mapa = None
linhas = 24
colunas = 48


async def agent_loop(server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))
        last_move = None
        acao = None
        while True:
            try:
                state = json.loads(await websocket.recv())
                if "map" in state:
                    mapa = state["map"]

                if "digdug" not in state or len(state["digdug"]) == 0:
                    continue

                if "enemies" not in state or len(state["enemies"]) == 0:
                    continue

                digdug_x, digdug_y = state["digdug"]
                enemies = state["enemies"]
                rocks = state["rocks"]

                mapa[digdug_x][digdug_y] = 0

                nearest_enemy = nearest_distance(state, mapa)
                if nearest_enemy is None:
                    continue

                enemy_x, enemy_y = state["enemies"][nearest_enemy]["pos"]

                # Se o gajo mais proximo for um fantasma foge
                if (
                    "traverse" in state["enemies"][nearest_enemy]
                    and state["enemies"][nearest_enemy]["traverse"] == True
                    and calc_dist(
                        state["digdug"], state["enemies"][nearest_enemy]["pos"]
                    )
                    <= 5
                ):
                    move = avoid_enemies(
                        state,
                        digdug_x,
                        digdug_y,
                        enemy_x,
                        enemy_y,
                        enemies,
                        last_move,
                    )
                    if move is not None:
                        await websocket.send(json.dumps({"cmd": "key", "key": move}))
                        last_move = move
                        continue

                acao = algoritmo_coiso(state, nearest_enemy, "greedy", mapa)

                if acao != None and len(acao) > 1:
                    # print(acao)
                    nextStepList = acao[1]
                    nextStep = [int(nextStepList[0]), int(nextStepList[1])]
                    next_x, next_y = nextStep[0], nextStep[1]

                    if dangerous_position(
                        state,
                        nearest_enemy,
                        next_x,
                        next_y,
                        digdug_x,
                        digdug_y,
                        enemies,
                    ):
                        # print("Dangerous position")
                        move = avoid_Rocks(
                            state,
                            mapa,
                            next_x,
                            next_y,
                            digdug_x,
                            digdug_y,
                            enemies,
                        )
                        if move is not None:
                            await websocket.send(
                                json.dumps({"cmd": "key", "key": move})
                            )
                            last_move = move
                            continue
                        move = avoid_enemies(
                            state,
                            digdug_x,
                            digdug_y,
                            enemy_x,
                            enemy_y,
                            enemies,
                            last_move,
                        )
                        if move is not None:
                            await websocket.send(
                                json.dumps({"cmd": "key", "key": move})
                            )
                            last_move = move
                            continue

                    move = avoid_Rocks(
                        state,
                        mapa,
                        next_x,
                        next_y,
                        digdug_x,
                        digdug_y,
                        enemies,
                    )
                    if move is not None:
                        # print("Avoiding rock")
                        await websocket.send(json.dumps({"cmd": "key", "key": move}))
                        last_move = move
                        continue

                    # Se ele estiver para ir contra o fogo do fygar foge
                    if in_the_fire(state, next_x, next_y):
                        # print("In the fire")
                        move = avoid_Rocks(
                            state,
                            mapa,
                            next_x,
                            next_y,
                            digdug_x,
                            digdug_y,
                            enemies,
                        )
                        if move is not None:
                            await websocket.send(
                                json.dumps({"cmd": "key", "key": move})
                            )
                            last_move = move
                            continue
                        move = avoid_enemies(
                            state,
                            digdug_x,
                            digdug_y,
                            enemy_x,
                            enemy_y,
                            enemies,
                            last_move,
                        )
                        if move is not None:
                            await websocket.send(
                                json.dumps({"cmd": "key", "key": move})
                            )
                            last_move = move
                            continue

                    if (
                        not_sandwiched(state, mapa, nearest_enemy, next_x, next_y)
                        == False
                    ):
                        # print("Sandwiched")
                        move = avoid_Rocks(
                            state,
                            mapa,
                            next_x,
                            next_y,
                            digdug_x,
                            digdug_y,
                            enemies,
                        )
                        if move is not None:
                            await websocket.send(
                                json.dumps({"cmd": "key", "key": move})
                            )
                            last_move = move
                            continue
                        move = avoid_enemies(
                            state,
                            digdug_x,
                            digdug_y,
                            enemy_x,
                            enemy_y,
                            enemies,
                            last_move,
                        )
                        if move is not None:
                            await websocket.send(
                                json.dumps({"cmd": "key", "key": move})
                            )
                            last_move = move
                            continue

                    if can_shoot(state, mapa, last_move, nearest_enemy):
                        # print("Can shoot")
                        await websocket.send(json.dumps({"cmd": "key", "key": "A"}))
                        last_move = "A"
                        continue
                    if (
                        (abs(digdug_x - enemy_x) < 3 and digdug_y == enemy_y)
                        or (abs(digdug_y - enemy_y) < 3 and digdug_x == enemy_x)
                        and can_shoot(state, mapa, last_move, nearest_enemy) == False
                    ):
                        # print("Enemy too close")
                        move = avoid_Rocks(
                            state,
                            mapa,
                            next_x,
                            next_y,
                            digdug_x,
                            digdug_y,
                            enemies,
                        )
                        if move is not None:
                            await websocket.send(
                                json.dumps({"cmd": "key", "key": move})
                            )
                            last_move = move
                            continue
                        move = avoid_enemies(
                            state,
                            digdug_x,
                            digdug_y,
                            enemy_x,
                            enemy_y,
                            enemies,
                            last_move,
                        )
                        if move is not None:
                            await websocket.send(
                                json.dumps({"cmd": "key", "key": move})
                            )
                            last_move = move
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

            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return


def dangerous_position(
    state, nearest_enemy, next_x, next_y, digdug_x, digdug_y, enemies
):
    # baixo - 2 ; direita - 1 ;esquerda - 3 ;cima - 0
    """(countRight, countLeft, countTop, countBottom) = count_enemies_in_each_side(
        digdug_x, digdug_y, enemies
    )"""

    # check if next position is 1 block away from enemy
    enemy_x, enemy_y = state["enemies"][nearest_enemy]["pos"]
    enemy_dir = state["enemies"][nearest_enemy]["dir"]

    if (
        enemy_x - 1 > 0
        or enemy_y - 1 > 0
        or enemy_x + 1 > colunas
        or enemy_y + 1 > linhas
    ):
        return False

    if enemy_dir == 1:
        if (
            (next_x, next_y)
            == ((enemy_x + 1, enemy_y + 1) or (enemy_x + 1, enemy_y - 1))
        ) or (
            (digdug_x, digdug_y) == ((enemy_x, enemy_y + 1) or (enemy_x, enemy_y - 1))
        ):
            return True
    elif enemy_dir == 3:
        if (
            (next_x, next_y)
            == ((enemy_x - 1, enemy_y + 1) or (enemy_x - 1, enemy_y - 1))
        ) or (
            (digdug_x, digdug_y) == ((enemy_x, enemy_y + 1) or (enemy_x, enemy_y - 1))
        ):
            return True
    elif enemy_dir == 0:
        if (
            (next_x, next_y)
            == ((enemy_x + 1, enemy_y - 1) or (enemy_x - 1, enemy_y - 1))
        ) or (
            (digdug_x, digdug_y) == ((enemy_x + 1, enemy_y) or (enemy_x - 1, enemy_y))
        ):
            return True
    elif enemy_dir == 2:
        if (
            (next_x, next_y)
            == ((enemy_x + 1, enemy_y + 1) or (enemy_x - 1, enemy_y + 1))
        ) or (
            (digdug_x, digdug_y) == ((enemy_x + 1, enemy_y) or (enemy_x - 1, enemy_y))
        ):
            return True
    return False


def in_the_fire(state, next_x, next_y):
    # baixo - 2 ; direita - 1 ;esquerda - 3 ;cima - 0
    for enemy in state["enemies"]:
        enemy_name = enemy["name"]
        if enemy_name == "Fygar":
            enemy_x, enemy_y = enemy["pos"]
            enemy_dir = enemy["dir"]
            if enemy_y == next_y:
                if (
                    enemy_dir == 1
                    and enemy_x + 4 <= colunas - 1
                    and (
                        enemy_x == next_x
                        or enemy_x + 1 == next_x
                        or enemy_x + 2 == next_x
                        or enemy_x + 3 == next_x
                        or enemy_x + 4 == next_x
                    )
                ):
                    return True
                elif (
                    enemy_dir == 3
                    and enemy_x - 4 >= 0
                    and (
                        enemy_x == next_x
                        or enemy_x - 1 == next_x
                        or enemy_x - 2 == next_x
                        or enemy_x - 3 == next_x
                        or enemy_x - 4 == next_x
                    )
                ):
                    return True
    return False


def check_other_enimies_while_shooting(state, mapa, nearest_enemy):
    enemies = state["enemies"]
    digdug_x, digdug_y = state["digdug"]
    shooting_distance = 2

    for enemy in enemies:
        if enemy != state["enemies"][nearest_enemy]:
            enemy_x, enemy_y = enemy["pos"]
            if enemy_x == digdug_x:
                if enemy_y > digdug_y:
                    if (
                        enemy_y - digdug_y <= shooting_distance
                        and enemy_y - 3 >= 0
                        and all(mapa[digdug_x][enemy_y - i] == 0 for i in range(1, 4))
                    ):
                        return False
                else:
                    if (
                        digdug_y - enemy_y <= shooting_distance
                        and enemy_y + 3 <= linhas - 1
                        and all(mapa[digdug_x][enemy_y + i] == 0 for i in range(1, 4))
                    ):
                        return False
            elif enemy_y == digdug_y:
                if (
                    enemy_x > digdug_x
                    and enemy_x - 3 >= 0
                    and all(mapa[enemy_x - i][digdug_y] == 0 for i in range(1, 4))
                ):
                    if enemy_x - digdug_x <= shooting_distance:
                        return False
                else:
                    if (
                        digdug_x - enemy_x <= shooting_distance
                        and enemy_x + 3 <= colunas - 1
                        and all(mapa[enemy_x + i][digdug_y] == 0 for i in range(1, 4))
                    ):
                        return False
    return True


def enemies_not_in_the_same_position(state, nearest_enemy):
    for enemy in state["enemies"]:
        if enemy != state["enemies"][nearest_enemy]:
            if enemy["pos"] == state["enemies"][nearest_enemy]["pos"]:
                return False
    return True


def not_sandwiched(state, mapa, nearest_enemy, digdug_x, digdug_y):
    nearest_x, nearest_y = state["enemies"][nearest_enemy]["pos"]

    for enemy in state["enemies"]:
        if enemy != state["enemies"][nearest_enemy]:
            enemy_x, enemy_y = enemy["pos"]
            if enemy_x == digdug_x == nearest_x:
                if (
                    enemy_y > digdug_y > nearest_y
                    or enemy_y < digdug_y < nearest_y
                    and abs(enemy_y - digdug_y) <= 3
                ):
                    return False
            elif enemy_y == digdug_y == nearest_y:
                if (
                    enemy_x > digdug_x > nearest_x
                    or enemy_x < digdug_x < nearest_x
                    and abs(enemy_x - digdug_x) <= 3
                ):
                    return False
    return True


def can_shoot(state, mapa, last_move, nearest_enemy):
    # print(last_move)
    shooting_distance = 3
    digdug_x, digdug_y = state["digdug"]
    enemy_x, enemy_y = state["enemies"][nearest_enemy]["pos"]
    if last_move == "d":  # ultima jogada foi para a direita e o inimigo esta a direita
        if (
            enemy_x > digdug_x
            and enemy_y == digdug_y
            and enemy_x - digdug_x <= shooting_distance
            and enemy_x - 3 >= 0
            and all(mapa[enemy_x - i][enemy_y] == 0 for i in range(1, 4))
            and enemies_not_in_the_same_position(state, nearest_enemy)
            and not_sandwiched(state, mapa, nearest_enemy, digdug_x, digdug_y)
        ):
            return True
    elif (
        last_move == "a"
    ):  # ultima jogada foi para a esquerda e o inimigo esta a esquerda
        if (
            enemy_x < digdug_x
            and enemy_y == digdug_y
            and digdug_x - enemy_x <= shooting_distance
            and enemy_x + 3 <= colunas - 1
            and all(mapa[enemy_x + i][enemy_y] == 0 for i in range(1, 4))
            and enemies_not_in_the_same_position(state, nearest_enemy)
            and not_sandwiched(state, mapa, nearest_enemy, digdug_x, digdug_y)
        ):
            return True
    elif last_move == "w":  # ultima jogada foi para cima e o inimigo esta acima
        if (
            enemy_y < digdug_y
            and enemy_x == digdug_x
            and digdug_y - enemy_y <= shooting_distance
            and enemy_y + 3 <= linhas - 1
            and all(mapa[digdug_x][enemy_y + i] == 0 for i in range(1, 4))
            and enemies_not_in_the_same_position(state, nearest_enemy)
            and not_sandwiched(state, mapa, nearest_enemy, digdug_x, digdug_y)
        ):
            return True
    elif last_move == "s":  # ultima jogada foi para baixo e o inimigo esta abaixo
        if (
            enemy_y > digdug_y
            and enemy_x == digdug_x
            and enemy_y - digdug_y <= shooting_distance
            and enemy_y - 3 >= 0
            and all(mapa[digdug_x][enemy_y - i] == 0 for i in range(1, 4))
            and enemies_not_in_the_same_position(state, nearest_enemy)
            and not_sandwiched(state, mapa, nearest_enemy, digdug_x, digdug_y)
        ):
            return True
    elif last_move == "A":  # ultima jogada foi para atirar
        if (
            enemy_x > digdug_x
            and enemy_y == digdug_y
            and enemy_x - digdug_x <= shooting_distance
            and enemy_x - 3 >= 0
            and all(mapa[enemy_x - i][enemy_y] == 0 for i in range(1, 4))
            and check_other_enimies_while_shooting(state, mapa, nearest_enemy)
            and enemies_not_in_the_same_position(state, nearest_enemy)
        ):
            return True
        elif (
            enemy_x < digdug_x
            and enemy_y == digdug_y
            and digdug_x - enemy_x <= shooting_distance
            and enemy_x + 3 <= colunas - 1
            and all(mapa[enemy_x + i][enemy_y] == 0 for i in range(1, 4))
            and check_other_enimies_while_shooting(state, mapa, nearest_enemy)
            and enemies_not_in_the_same_position(state, nearest_enemy)
        ):
            return True
        elif (
            enemy_y < digdug_y
            and enemy_x == digdug_x
            and digdug_y - enemy_y <= shooting_distance
            and enemy_y + 3 <= linhas - 1
            and all(mapa[enemy_x][enemy_y + i] == 0 for i in range(1, 4))
            and check_other_enimies_while_shooting(state, mapa, nearest_enemy)
            and enemies_not_in_the_same_position(state, nearest_enemy)
        ):
            return True
        elif (
            enemy_y > digdug_y
            and enemy_x == digdug_x
            and enemy_y - digdug_y <= shooting_distance
            and enemy_y - 3 >= 0
            and all(mapa[enemy_x][enemy_y - i] == 0 for i in range(1, 4))
            and check_other_enimies_while_shooting(state, mapa, nearest_enemy)
            and enemies_not_in_the_same_position(state, nearest_enemy)
        ):
            return True
    return False


def avoid_Rocks(state, mapa, next_x, next_y, digdug_x, digdug_y, enemies):
    (countRight, countLeft, countTop, countBottom) = count_enemies_in_each_side(
        digdug_x, digdug_y, enemies
    )

    for rock in state["rocks"]:
        rock_x, rock_y = rock["pos"]
        if rock_x == next_x and rock_y == next_y:
            if digdug_x < rock_x and digdug_y == rock_y:
                if countTop < countBottom and digdug_y > 0:
                    return "w"
                else:
                    return "s"
            elif digdug_x > rock_x and digdug_y == rock_y:
                if countTop < countBottom and digdug_y > 0:
                    return "w"
                else:
                    return "s"
            elif digdug_y < rock_y and digdug_x == rock_x:
                if countLeft < countRight and digdug_x > 0:
                    return "a"
                else:
                    return "d"
            elif digdug_y > rock_y and digdug_x == rock_x:
                if countLeft < countRight and digdug_x > 0:
                    return "a"
                else:
                    return "d"

    return None


def avoid_enemies(
    state,
    digdug_x,
    digdug_y,
    nearest_enemy_x,
    nearest_enemy_y,
    enemies,
    last_move,
):
    count = count_enemies_in_each_side(digdug_x, digdug_y, enemies)

    fire_right = in_the_fire(state, digdug_x + 1, digdug_y)
    fire_left = in_the_fire(state, digdug_x - 1, digdug_y)
    fire_up = in_the_fire(state, digdug_x, digdug_y - 1)
    fire_down = in_the_fire(state, digdug_x, digdug_y + 1)

    min = math.inf
    minIndex = 0
    for i in range(4):
        if count[i] < min:
            min = count[i]
            minIndex = i

    (countRight, countLeft, countTop, countBottom) = count

    if digdug_x == 0 or digdug_x == colunas - 1:
        if last_move == "a" or last_move == "d":
            if (
                countTop < countBottom
                and digdug_y > 0
                and not in_the_fire(state, digdug_x, digdug_y + 1)
            ):
                return "w"
            else:
                return "s"

    elif digdug_y == 0 or digdug_y == linhas - 1:
        if last_move == "w" or last_move == "s":
            if countLeft < countRight and not in_the_fire(
                state, digdug_x - 1, digdug_y
            ):
                return "a"
            else:
                return "d"

    enemyOnRight = False
    enemyOnLeft = False
    enemyOnTop = False
    enemyOnBottom = False

    if digdug_x < nearest_enemy_x and digdug_y == nearest_enemy_y:
        # print("enemy on right")
        enemyOnRight = True
    elif digdug_x > nearest_enemy_x and digdug_y == nearest_enemy_y:
        # print("enemy on left")
        enemyOnLeft = True
    elif digdug_y < nearest_enemy_y and digdug_x == nearest_enemy_x:
        # print("enemy on bottom")
        enemyOnBottom = True
    elif digdug_y > nearest_enemy_y and digdug_x == nearest_enemy_x:
        # print("enemy on top")
        enemyOnTop = True

    if enemyOnRight:
        if minIndex == 1 and not fire_left:
            return "a"
        elif minIndex == 2 and not fire_up:
            return "w"
        elif minIndex == 3 and not fire_down:
            return "s"
    elif enemyOnLeft:
        if minIndex == 0 and not fire_right:
            return "d"
        elif minIndex == 2 and not fire_up:
            return "w"
        elif minIndex == 3 and not fire_down:
            return "s"
    elif enemyOnTop:
        if minIndex == 0 and not fire_right:
            return "d"
        elif minIndex == 1 and not fire_left:
            return "a"
        elif minIndex == 3 and not fire_down:
            return "s"
    elif enemyOnBottom:
        if minIndex == 0 and not fire_right:
            return "d"
        elif minIndex == 1 and not fire_left:
            return "a"
        elif minIndex == 2 and not fire_up:
            return "w"


def count_enemies_in_each_side(digdug_x, digdug_y, enemies):
    countR = 0
    countL = 0
    countT = 0
    countB = 0

    for enemy in enemies:
        enemy_x, enemy_y = enemy["pos"]
        if abs(enemy_x - digdug_x) <= 5 and abs(enemy_y - digdug_y) <= 5:
            if enemy_x < digdug_x:
                countL += 1
            elif enemy_x > digdug_x:
                countR += 1
            elif enemy_y < digdug_y:
                countT += 1
            elif enemy_y > digdug_y:
                countB += 1

    return (countR, countL, countT, countB)


def algoritmo_coiso(state, enemy, strategy, mapa):
    enemy_x, enemy_y = state["enemies"][enemy]["pos"]
    digdug_x, digdug_y = state["digdug"]
    enemy_name = state["enemies"][enemy]["name"]
    enemy_dir = state["enemies"][enemy]["dir"]
    # baixo - 2 ; direita - 1 ;esquerda - 3 ;cima - 0
    # Acoes para o fygar
    if enemy_name == "Fygar":
        if (  # se o digdug esta a direita do fygar
            enemy_x < digdug_x
            and enemy_dir == 1
            and enemy_y == digdug_y
            and enemy_y - 2 >= 0
            and digdug_x - enemy_x <= 4
            and all(mapa[enemy_x + i][enemy_y] == 0 for i in range(1, 4))
        ):
            print("fygar a esquerda")
            enemy_y -= 2
        elif (
            enemy_x > digdug_x
            and enemy_dir == 3
            and enemy_y + 2 <= linhas - 1
            and enemy_y == digdug_y
            and enemy_x - digdug_x <= 4
            and all(mapa[enemy_x + i][enemy_y] == 0 for i in range(1, 4))
        ):
            print("fygar a direita")
            enemy_y += 2
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
        if enemy_name == "Fygar" and enemy_x + 3 <= colunas - 1:
            enemy_x += 3
        else:
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
        if enemy_name == "Fygar" and enemy_x - 3 >= 0:
            enemy_x -= 3
        else:
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

    return astar(mapa, (digdug_x, digdug_y), (enemy_x, enemy_y))


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


def calc_dist(pos1, pos2):
    return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)


loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))
