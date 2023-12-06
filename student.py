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
                        await websocket.send(json.dumps({"cmd": "key", "key": move}))
                        last_move = move
                        continue

                    move = avoid_enemies(
                        state, digdug_x, digdug_y, enemy_x, enemy_y, enemies, rocks
                    )
                    if move is not None:
                        await websocket.send(json.dumps({"cmd": "key", "key": move}))
                        last_move = move
                        continue

                acao = algoritmo_search(state, nearest_enemy, "greedy", mapa)

                if acao != None and len(acao) > 1:
                    # print(acao)
                    nextStepList = acao[1]
                    nextStep = [int(nextStepList[0]), int(nextStepList[1])]
                    next_x, next_y = nextStep[0], nextStep[1]

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

                    """ if dangerous_position(
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
                            state, digdug_x, digdug_y, enemy_x, enemy_y, enemies, rocks
                        )
                        if move is not None:
                            await websocket.send(
                                json.dumps({"cmd": "key", "key": move})
                            )
                            last_move = move
                            continue """

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
                            state, digdug_x, digdug_y, enemy_x, enemy_y, enemies, rocks
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
                            state, digdug_x, digdug_y, enemy_x, enemy_y, enemies, rocks
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
                            state, digdug_x, digdug_y, enemy_x, enemy_y, enemies, rocks
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


def avoid_Rocks(state, mapa, next_x, next_y, digdug_x, digdug_y, enemies):
    (
        countEnemyRight,
        countEnemyLeft,
        countEnemyTop,
        countEnemyBottom,
    ) = count_enemies_in_each_side(digdug_x, digdug_y, enemies)

    (
        countRockRight,
        countRockLeft,
        countRockTop,
        countRockBottom,
    ) = count_rocks_in_each_side(digdug_x, digdug_y, state["rocks"])

    count_rocks = (
        countRockRight,
        countRockLeft,
        countRockTop,
        countRockBottom,
    )

    count_rocks_enemies = [
        countEnemyRight + countRockRight,
        countEnemyLeft + countRockLeft,
        countEnemyTop + countRockTop,
        countEnemyBottom + countRockBottom,
    ]

    fire_right = in_the_fire(state, digdug_x + 1, digdug_y)
    fire_left = in_the_fire(state, digdug_x - 1, digdug_y)
    fire_up = in_the_fire(state, digdug_x, digdug_y - 1)
    fire_down = in_the_fire(state, digdug_x, digdug_y + 1)

    enemies_coord = []
    for enemy in enemies:
        enemy_x, enemy_y = enemy["pos"]
        enemies_coord.append([enemy_x, enemy_y])

    rocks_coord = []
    for rock in state["rocks"]:
        rock_x, rock_y = rock["pos"]
        rocks_coord.append([rock_x, rock_y])

    for rock in state["rocks"]:
        rock_x, rock_y = rock["pos"]

        if digdug_x == rock_x and digdug_y > rock_y:
            coord_between_rock_digdug = []
            suicide = True
            for i in range(rock_y + 1, digdug_y):
                coord_between_rock_digdug.append([rock_x, i])

            for coord in coord_between_rock_digdug:
                if mapa[coord[0]][coord[1]] == 1:
                    suicide = False

            if suicide:
                if (
                    countEnemyLeft < countEnemyRight
                    and digdug_x > 0
                    and [digdug_x - 1, digdug_y] not in enemies_coord
                    and [digdug_x - 1, digdug_y] not in rocks_coord
                ):
                    return "a"
                else:
                    return "d"

        if next_x == rock_x and next_y == rock_y:
            minIndex = None
            if sum([countRockRight, countRockLeft, countRockTop, countRockBottom]) != 0:
                min = math.inf

                for i in range(4):
                    if (
                        (
                            (i == 0 and fire_right)
                            or (i == 0 and digdug_x == colunas - 1)
                        )
                        or ((i == 1 and fire_left) or (i == 1 and digdug_x == 0))
                        or ((i == 2 and fire_up) or (i == 2 and digdug_y == 0))
                        or (
                            (i == 3 and fire_down)
                            or (i == 3 and digdug_y == linhas - 1)
                        )
                    ):
                        continue
                    elif countRockRight > 0 and i == 1:
                        continue
                    elif countRockLeft > 0 and i == 0:
                        continue
                    elif countRockTop > 0 and i == 3:
                        continue
                    elif countRockBottom > 0 and i == 2:
                        continue
                    elif [digdug_x + 1, digdug_y] in enemies_coord and i == 0:
                        continue
                    elif [digdug_x - 1, digdug_y] in enemies_coord and i == 1:
                        continue
                    elif [digdug_x, digdug_y - 1] in enemies_coord and i == 2:
                        continue
                    elif [digdug_x, digdug_y + 1] in enemies_coord and i == 3:
                        continue
                    elif [digdug_x + 1, digdug_y] in rocks_coord and i == 0:
                        continue
                    elif [digdug_x - 1, digdug_y] in rocks_coord and i == 1:
                        continue
                    elif [digdug_x, digdug_y - 1] in rocks_coord and i == 2:
                        continue
                    elif [digdug_x, digdug_y + 1] in rocks_coord and i == 3:
                        continue

                    if count_rocks[i] < min:
                        min = count_rocks[i]
                        minIndex = i

            if minIndex == 0:
                return "d"
            elif minIndex == 1:
                return "a"
            elif minIndex == 2:
                return "w"
            elif minIndex == 3:
                return "s"

    return None


def avoid_enemies(
    state,
    digdug_x,
    digdug_y,
    nearest_enemy_x,
    nearest_enemy_y,
    enemies,
    rocks,
):
    count_enemies1 = count_enemies_in_each_side(digdug_x, digdug_y, enemies)

    count_enemies = [
        count_enemies1[2],  # top
        count_enemies1[3],  # bottom
        count_enemies1[0],  # right
        count_enemies1[1],  # left
    ]

    fire_right = (
        in_the_fire(state, digdug_x + 1, digdug_y)
        and in_the_fire(state, digdug_x + 2, digdug_y)
        and in_the_fire(state, digdug_x + 3, digdug_y)
    )
    fire_left = (
        in_the_fire(state, digdug_x - 1, digdug_y)
        and in_the_fire(state, digdug_x - 2, digdug_y)
        and in_the_fire(state, digdug_x - 3, digdug_y)
    )
    fire_up = (
        in_the_fire(state, digdug_x, digdug_y - 1)
        and in_the_fire(state, digdug_x, digdug_y - 2)
        and in_the_fire(state, digdug_x, digdug_y - 3)
    )
    fire_down = (
        in_the_fire(state, digdug_x, digdug_y + 1)
        and in_the_fire(state, digdug_x, digdug_y + 2)
        and in_the_fire(state, digdug_x, digdug_y + 3)
    )

    enemies_coord = []
    for enemy in enemies:
        enemy_x, enemy_y = enemy["pos"]
        enemies_coord.append([enemy_x, enemy_y])

    rocks_coord = []
    for rock in rocks:
        rock_x, rock_y = rock["pos"]
        rocks_coord.append([rock_x, rock_y])

    min = math.inf
    minIndex = 0
    for i in range(4):
        if (
            ((i == 0 and fire_up) or (i == 0 and digdug_y == 2))
            or ((i == 1 and fire_down) or (i == 1 and digdug_y == linhas - 3))
            or ((i == 2 and fire_right) or (i == 2 and digdug_x == colunas - 3))
            or ((i == 3 and fire_left) or (i == 3 and digdug_x == 2))
        ):
            continue
        elif [digdug_x + 1, digdug_y] in enemies_coord and i == 2:
            continue
        elif [digdug_x - 1, digdug_y] in enemies_coord and i == 3:
            continue
        elif [digdug_x, digdug_y - 1] in enemies_coord and i == 0:
            continue
        elif [digdug_x, digdug_y + 1] in enemies_coord and i == 1:
            continue
        elif [digdug_x + 1, digdug_y] in rocks_coord and i == 2:
            continue
        elif [digdug_x - 1, digdug_y] in rocks_coord and i == 3:
            continue
        elif [digdug_x, digdug_y - 1] in rocks_coord and i == 0:
            continue
        elif [digdug_x, digdug_y + 1] in rocks_coord and i == 1:
            continue

        if count_enemies[i] < min:
            min = count_enemies[i]
            minIndex = i

    enemyOnRight = False
    enemyOnLeft = False
    enemyOnTop = False
    enemyOnBottom = False

    if digdug_x < nearest_enemy_x and digdug_y == nearest_enemy_y:
        enemyOnRight = True
    elif digdug_x > nearest_enemy_x and digdug_y == nearest_enemy_y:
        enemyOnLeft = True
    elif digdug_y < nearest_enemy_y and digdug_x == nearest_enemy_x:
        enemyOnBottom = True
    elif digdug_y > nearest_enemy_y and digdug_x == nearest_enemy_x:
        enemyOnTop = True

    # top, bottom, right, left
    if enemyOnRight:
        if minIndex == 0:
            return "w"
        elif minIndex == 1:
            return "s"
        elif minIndex == 3:
            return "a"
    elif enemyOnLeft:
        if minIndex == 0:
            return "w"
        elif minIndex == 1:
            return "s"
        elif minIndex == 2:
            return "d"
    elif enemyOnTop:
        if minIndex == 1:
            return "s"
        elif minIndex == 2:
            return "d"
        elif minIndex == 3:
            return "a"
    elif enemyOnBottom:
        if minIndex == 0:
            return "w"
        elif minIndex == 2:
            return "d"
        elif minIndex == 3:
            return "a"


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
            elif enemy_x == digdug_x and nearest_y == digdug_y:
                if abs(digdug_y - enemy_y) <= 3:
                    return False
            elif enemy_y == digdug_y and nearest_x == digdug_x:
                if abs(digdug_x - enemy_x) <= 3:
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


def algoritmo_search(state, enemy, strategy, mapa):
    enemy_x, enemy_y = state["enemies"][enemy]["pos"]
    digdug_x, digdug_y = state["digdug"]
    enemy_name = state["enemies"][enemy]["name"]
    enemy_dir = state["enemies"][enemy]["dir"]

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
        if enemy_name == "Fygar":
            if enemy_x + 3 <= colunas - 1:
                enemy_x += 3
            else:
                enemy_y += 2
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
        if enemy_name == "Fygar":
            if enemy_x - 3 >= 0:
                enemy_x -= 3
            else:
                enemy_y -= 2
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

    return astar(mapa, (digdug_x, digdug_y), (enemy_x, enemy_y), state)


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
            if enemy_x > digdug_x:
                countR += 1
            if enemy_y < digdug_y:
                countT += 1
            if enemy_y > digdug_y:
                countB += 1

    return (countR, countL, countT, countB)


def count_rocks_in_each_side(digdug_x, digdug_y, rocks):
    countR = 0
    countL = 0
    countT = 0
    countB = 0

    for rock in rocks:
        rock_x, rock_y = rock["pos"]
        if abs(rock_x - digdug_x) <= 1 and abs(rock_y - digdug_y) <= 1:
            if rock_x == digdug_x - 1:
                countL += 1
            elif rock_x == digdug_x + 1:
                countR += 1
            elif rock_y == digdug_y - 1:
                countT += 1
            elif rock_y == digdug_y + 1:
                countB += 1

    return (countR, countL, countT, countB)


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
