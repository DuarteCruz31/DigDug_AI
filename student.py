import asyncio
import getpass
import json
import os
import websockets
import numpy as np
from collections import deque

async def agent_loop(server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        last_move = "d"
        i = 0
        mapa = None
        closest_enemy = None

        while True:
            try:
                state = json.loads(await websocket.recv())
                if i == 0:
                    mapa = state["map"]
                    i += 1
                else: 
                    if 'digdug' not in state:
                        continue

                    if 'enemies' not in state:
                        continue

                    closest_enemy = find_closest_enemy(state["digdug"], state["enemies"], mapa)
                    
                    digdug_x, digdug_y = state["digdug"]

                    mapa[digdug_x][digdug_y] = 0

                    enemies = state["enemies"]
                    move, shoot = decide_digdug_move(digdug_x, digdug_y, enemies, last_move, mapa, closest_enemy)

                    if move:
                        await websocket.send(json.dumps({"cmd": "key", "key": move}))
                        last_move = move
                    if shoot:
                        await websocket.send(json.dumps({"cmd": "key", "key": "A"}))

            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return


def decide_digdug_move(digdug_x, digdug_y, enemies, last_move, mapa, closest_enemy):
    move = None
    shoot = False
    # Encontre o inimigo mais próximo
    closest_distance = float('inf')
    closest_enemy = None

    for enemy in enemies:
        enemy_x, enemy_y = enemy['pos']
        distance = abs(digdug_x - enemy_x) + abs(digdug_y - enemy_y)

        if distance < closest_distance:
            closest_distance = distance
            closest_enemy = enemy

    if closest_enemy is not None:
        enemy_x, enemy_y = closest_enemy['pos']
        if in_same_tunnel(digdug_x, digdug_y, enemy_x, enemy_y, mapa):
            print("in same tunnel")
            if abs(digdug_x - enemy_x) <= 3 and abs(digdug_y - enemy_y) == 0:
                move = avoid_enemy_horizontal(digdug_x, enemy_x)
                shoot = True
                print("shoot")
            elif abs(digdug_y - enemy_y) <= 3 and abs(digdug_x - enemy_x) == 0:
                move = avoid_enemy_vertical(digdug_y, enemy_y)
                shoot = True
                print("shoot")
            else:
                move = move_towards_enemy(digdug_x, digdug_y, enemy_x, enemy_y, last_move)
        else:
            move = move_towards_enemy(digdug_x, digdug_y, enemy_x, enemy_y, last_move)
    if not move:
        move = " "

    return move, shoot


def in_same_tunnel(start_x, start_y, end_x, end_y, mapa):
    path = get_shortest_path(start_x, start_y, end_x, end_y, mapa)
    if path is None:
        return False

    for x, y in path:
        if mapa[x][y] == 1:
            return False

    return True

def get_shortest_path(start_x, start_y, end_x, end_y, mapa):
    queue = deque()
    queue.append((start_x, start_y))
    visited = set()
    visited.add((start_x, start_y))
    path = {}

    while queue:
        current_x, current_y = queue.popleft()
        if current_x == end_x and current_y == end_y:
            break

        for x, y in get_adjacent_tiles(current_x, current_y, mapa):
            if (x, y) not in visited:
                queue.append((x, y))
                visited.add((x, y))
                path[(x, y)] = (current_x, current_y)

    return path

def get_adjacent_tiles(x, y, mapa):
    adjacent_tiles = []
    if x > 0 and mapa[x - 1][y] == 1:
        adjacent_tiles.append((x - 1, y))
    if x < len(mapa) - 1 and mapa[x + 1][y] == 1:
        adjacent_tiles.append((x + 1, y))
    if y > 0 and mapa[x][y - 1] == 1:
        adjacent_tiles.append((x, y - 1))
    if y < len(mapa[0]) - 1 and mapa[x][y + 1] == 1:
        adjacent_tiles.append((x, y + 1))
    return adjacent_tiles

def find_closest_enemy(digdug, enemies, mapa):
    closest_enemy = None
    closest_distance = float("inf")

    for enemy in enemies:
        enemy_x, enemy_y = enemy['pos']
        distance = get_distance(digdug[0], digdug[1], enemy_x, enemy_y, mapa)

        if distance < closest_distance:
            closest_distance = distance
            closest_enemy = (enemy_x, enemy_y)

    return closest_enemy

def get_distance(x1, y1, x2, y2, mapa):
    path = get_shortest_path(x1, y1, x2, y2, mapa)
    return len(path) if path is not None else float("inf")

def avoid_enemy_horizontal(digdug_x, enemy_x):
    if digdug_x < enemy_x:
        return "a"
    elif digdug_x > enemy_x:
        return "d"


def avoid_enemy_vertical(digdug_y, enemy_y):
    if digdug_y < enemy_y:
        return "w"
    elif digdug_y > enemy_y:
        return "s"


def move_towards_enemy(digdug_x, digdug_y, enemy_x, enemy_y, last_move):
    if digdug_x < enemy_x:
        return "d"
    elif digdug_x > enemy_x:
        return "a"
    elif digdug_y < enemy_y:
        return "s"
    elif digdug_y > enemy_y:
        return "w"
    return last_move

loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))
