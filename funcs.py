import numpy as np
import math
from collections import deque

def in_same_tunnel(start_x, start_y, end_x, end_y, mapa):
    path = get_shortest_path(start_x, start_y, end_x, end_y, mapa)
    if path is None:
        return False

    for x, y in path:
        if mapa[x][y] == 1:
            return False

    return True

def get_shortest_path(start_x, start_y, end_x, end_y, grid):
    def heuristic(node):
        x, y = node
        return abs(x - end_x) + abs(y - end_y)

    open_list = [(start_x, start_y)]
    closed_list = set()
    came_from = {}
    g_score = {(x, y): float('inf') for x in range(len(grid)) for y in range(len(grid[0]))}
    g_score[(start_x, start_y)] = 0
    f_score = {(x, y): float('inf') for x in range(len(grid)) for y in range(len(grid[0]))}
    f_score[(start_x, start_y)] = heuristic((start_x, start_y))

    while open_list:
        current = min(open_list, key=lambda node: f_score[node])
        if current == (end_x, end_y):
            path = []
            while current in came_from:
                path.insert(0, current)
                current = came_from[current]
            return path

        open_list.remove(current)
        closed_list.add(current)

        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            x, y = current[0] + dx, current[1] + dy
            if x < 0 or x >= len(grid) or y < 0 or y >= len(grid[0]) or grid[x][y] == 1:
                continue

            neighbor = (x, y)

            tentative_g_score = g_score[current] + 1

            if neighbor not in open_list:
                open_list.append(neighbor)
            elif tentative_g_score >= g_score[neighbor]:
                continue

            came_from[neighbor] = current
            g_score[neighbor] = tentative_g_score
            f_score[neighbor] = g_score[neighbor] + heuristic(neighbor)

    return None  # No path found

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
    digdug_x, digdug_y = digdug
    closest_enemy = None
    closest_distance = float('inf')
    for enemy in enemies:
        enemy_x, enemy_y = enemy['pos']
        if enemy['id'] == 0:
            continue
        distance = get_distance(digdug_x, digdug_y, enemy_x, enemy_y)
        if distance < closest_distance:
            closest_enemy = [enemy_x, enemy_y]
            closest_distance = distance
    return closest_enemy

def get_distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

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

def move_away_from_enemy(digdug_x, digdug_y, enemy_x, enemy_y, last_move):
    # Calculate the direction to move away from the enemy
    dx = digdug_x - enemy_x
    dy = digdug_y - enemy_y

    if dx < 0:
        move = "a"
    elif dx > 0:
        move = "d"
    elif dy < 0:
        move = "w"
    elif dy > 0:
        move = "s"
    else:
        # If the enemy is on top of Dig Dug, choose a random direction
        possible_moves = ["w", "a", "s", "d"]
        possible_moves.remove(last_move)  # Avoid going back the way we came
        move = np.random.choice(possible_moves)

    return move