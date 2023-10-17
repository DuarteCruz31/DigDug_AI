import asyncio
import getpass
import json
import os
import websockets
from collections import deque
from digdug import *
import math
from tree_search import *
from digdug import *

movimentos = None


async def agent_loop(server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        i = 0
        while True:
            try:
                state = json.loads(await websocket.recv())
                if i == 0:
                    mapa = state["map"]
                    i += 1
                else:
                    if "digdug" not in state:
                        continue

                    if "enemies" not in state:
                        continue

                    if i == 1:
                        digdug_x, digdug_y = state["digdug"]
                        personagens = {"digdug": (digdug_x, digdug_y)}
                        for enemy in state["enemies"]:
                            enemy_x, enemy_y = enemy["pos"]
                            personagens[enemy["id"]] = (enemy_x, enemy_y)

                        # Tamanho da matriz
                        linhas = 48
                        colunas = 24

                        # Lista para armazenar os movimentos no formato [(<inicio>, <fim>, 1)]
                        possible_moves = []

                        # Adicionar movimentos para cima
                        for linha in range(linhas):
                            for coluna in range(colunas):
                                if linha > 0:
                                    inicio = str((linha, coluna))
                                    fim = str((linha - 1, coluna))
                                    possible_moves.append((inicio, fim, 1))

                        # Adicionar movimentos para baixo
                        for linha in range(linhas):
                            for coluna in range(colunas):
                                if linha < linhas - 1:
                                    inicio = str((linha, coluna))
                                    fim = str((linha + 1, coluna))
                                    possible_moves.append((inicio, fim, 1))

                        # Adicionar movimentos para a esquerda
                        for linha in range(linhas):
                            for coluna in range(colunas):
                                if coluna > 0:
                                    inicio = str((linha, coluna))
                                    fim = str((linha, coluna - 1))
                                    possible_moves.append((inicio, fim, 1))

                        # Adicionar movimentos para a direita
                        for linha in range(linhas):
                            for coluna in range(colunas):
                                if coluna < colunas - 1:
                                    inicio = str((linha, coluna))
                                    fim = str((linha, coluna + 1))
                                    possible_moves.append((inicio, fim, 1))

                        coordenadas = {}
                        for linha in range(linhas):
                            for coluna in range(colunas):
                                coordenada = (linha, coluna)
                                coordenada_str = f"({linha}, {coluna})"
                                coordenadas[coordenada_str] = coordenada

                        movimentos = DigDug(
                            # Ligacoes por estrada
                            possible_moves,
                            coordenadas,
                        )
                        i += 1

                    if i == 2:
                        for enemy in state["enemies"]:
                            p = SearchProblem(
                                movimentos,
                                str(tuple(state["digdug"])),
                                str(tuple(enemy["pos"])),
                            )
                            t = SearchTree(p, "breadth")
                            print(t.search(), t.cost)
                        i += 1

            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return


loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))
