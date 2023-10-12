import asyncio
import getpass
import json
import os
import websockets
import pygame
import math

async def agent_loop(server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        last_move = "d"

        while True:
            try:
                state = json.loads(await websocket.recv())

                if 'digdug' in state:
                    digdug_x, digdug_y = state['digdug']
                else:
                    digdug_x, digdug_y = [0, 0]

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
        
        horizontal_distance = abs(digdug_x - enemy_x)
        vertical_distance = abs(digdug_y - enemy_y)

        if horizontal_distance <= 3 and vertical_distance == 0:
            # If an enemy is too close horizontally, move away
            move = avoid_enemy_horizontal(digdug_x, enemy_x)
            if enemy['id'] not in enemies_shot:
                shoot = True
                enemies_shot.add(enemy['id'])
            break
        elif vertical_distance <= 3 and horizontal_distance == 0:
            # If an enemy is too close vertically, move away
            move = avoid_enemy_vertical(digdug_y, enemy_y)
            if enemy['id'] not in enemies_shot:
                shoot = True
                enemies_shot.add(enemy['id'])
            break
        else:
            # If no enemies are close, move towards the closest one
            move = move_towards_enemy(digdug_x, digdug_y, enemy_x, enemy_y, last_move)

    # If no move was decided, move forward
    if not move:
        move = "d"

    return move, shoot

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
