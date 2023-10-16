import asyncio
import getpass
import json
import os
from turtle import distance, position
import websockets
import pygame
import math

async def agent_loop(server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        yourmap = Map
        
        enemy_counter = 0

        while True:
            try:
                state = json.loads(await websocket.recv())

                

                if 'digdug' in state:
                    digdug_x, digdug_y = state['digdug']
                    position = Block(digdug_x,digdug_y)
                    yourmap.change_position(position)

                else:
                    digdug_x, digdug_y = [0, 0]
                    position = Block(digdug_x,digdug_y)
                    yourmap.change_position(position)



                if 'enemies' in state:
                    enemies = state['enemies']

                
                for enemy in enemies:
                    enemymap = Map
                    enemy_counter += 1
                    enemy_x, enemy_y = enemy['pos']
                    enemy_position = Block(enemy_x,enemy_y)
                    enemymap.change_position(enemy_position)
                    
                    move =  move_towards_enemy(digdug_x , digdug_y , enemy_x , enemy_y)
                

            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return
    


# def decide_digdug_move(digdug_x, digdug_y, enemies, last_move):
#     move = None
#     shoot = False

#     enemies_shot = set()

#     for enemy in enemies:
#         enemy_x, enemy_y = enemy['pos']

    #         horizontal_distance = abs(digdug_x - enemy_x)
    #         vertical_distance = abs(digdug_y - enemy_y)

#         if horizontal_distance == 0:
            

    
#         if enemy['id'] not in enemies_shot:
#             shoot = True
#             enemies_shot.add(enemy['id'])
#             break
#         elif enemy['id'] not in enemies_shot:
#             shoot = True
#             enemies_shot.add(enemy['id'])
#             break
#         else:
#             # If no enemies are close, move towards the closest one
#             move = move_towards_enemy(digdug_x, digdug_y, enemy_x, enemy_y, last_move)

#     # If no move was decided, move forward
#     if not move:
#         move = "d"

#     return move, shoot

# def avoid_enemy_horizontal(digdug_x, enemy_x):
#     if digdug_x < enemy_x:
#         return "a"
#     elif digdug_x > enemy_x:
#         return "d"

# def avoid_enemy_vertical(digdug_y, enemy_y):
#     if digdug_y < enemy_y:
#         return "w"
#     elif digdug_y > enemy_y:
#         return "s"

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

class Block:
    def __init__(self, x , y):
        self.x = x
        self.y = y
        self.used = 0

    def distance(self , other_block):
        h = abs(self.x - other_block.x)
        v = abs(self.y - other_block.y)
        return [h,v]
    
class Map:
    def __init__(self):  
        self.coordinates = Block(1,0)
        self.tracker = []


    def change_position(self,new_coordinates):
        self.tracker.append(self.coordinates)
        self.coordinates.used += 1
        self.coordinates = new_coordinates
        


    
            
    


loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))