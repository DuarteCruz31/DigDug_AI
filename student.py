import asyncio
import getpass
import json
import os
import websockets
import numpy as np

mapa = np.zeros((50, 100))

async def agent_loop(server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        last_move = "d"

        while True:
            try:
                state = json.loads(await websocket.recv())

                if 'digdug' in state:
                    digdug_x, digdug_y = state['digdug']

                    mapa[digdug_x, digdug_y] = 1
                else:
                    digdug_x, digdug_y = [0, 0]
                    
                    mapa[0, 0] = 1


                if 'enemies' in state:
                    enemies = state['enemies']
                    move, shoot = decide_digdug_move(digdug_x, digdug_y, enemies, last_move)

                    if move:
                        await websocket.send(json.dumps({"cmd": "key", "key": move}))
                        last_move = move

                    if shoot:
                        await websocket.send(json.dumps({"cmd": "key", "key": "A"}))

            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return

def decide_digdug_move(digdug_x, digdug_y, enemies, last_move):
    move = None
    shoot = False

    enemies_shot = set()

    for enemy in enemies:
        enemy_x, enemy_y = enemy['pos']

        mapa[enemy_x, enemy_y] = 1

        horizontal_distance = abs(digdug_x - enemy_x)
        vertical_distance = abs(digdug_y - enemy_y)

        if horizontal_distance <= 3 and vertical_distance == 0 and same_tunnel(digdug_x, digdug_y, enemy_x, enemy_y):
            move = avoid_enemy_horizontal(digdug_x, enemy_x)
            if enemy['id'] not in enemies_shot:
                shoot = True
                enemies_shot.add(enemy['id'])
            break
        elif vertical_distance <= 3 and horizontal_distance == 0 and same_tunnel(digdug_x, digdug_y, enemy_x, enemy_y):
            move = avoid_enemy_vertical(digdug_y, enemy_y)
            if enemy['id'] not in enemies_shot:
                shoot = True
                enemies_shot.add(enemy['id'])
            break
        elif same_tunnel(digdug_x, digdug_y, enemy_x, enemy_y):
            move = move_towards_enemy(digdug_x, digdug_y, enemy_x, enemy_y, last_move)
        else:
            shoot = False
            move = move_towards_enemy(digdug_x, digdug_y, enemy_x, enemy_y, last_move)

    if not move:
        # Se nao for tomada decisao o gajo fica no mesmo sitio
        move = " "

    return move, shoot


def same_tunnel(start_x, start_y, end_x, end_y):
    if start_x == end_x:
        min_y = min(start_y, end_y)
        max_y = max(start_y, end_y)
        for y in range(min_y, max_y):
            if mapa[start_x][y] == 0:
                return False
    elif start_y == end_y:
        min_x = min(start_x, end_x)
        max_x = max(start_x, end_x)
        for x in range(min_x, max_x):
            if mapa[x][start_y] == 0:
                return False

    return True


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
