import heapq
from auxiliarFuncs import *

POINTS_ROCKS = 10000
POINTS_FYGAR = 10000
POINTS_WALL = 5
POINTS_POOKA = 10000
POINTS_GHOST = 10000
POINTS_AVOID = 10000


def calculate_cost_normal(maze, position, state, nearest_enemy):
    """
    Calculates the normal cost of moving to a specific position without avoiding enemies.

    This function calculates the normal cost of moving to a specific position on the game map without
    considering the presence of enemies. The cost is influenced by various factors, such as the type of tile
    at the position, the presence of rocks, and the proximity to ghosts.

    Args:
        maze (list): A 2D list representing the game map where 1 indicates a wall and 0 indicates an open space.
        position (tuple): A tuple representing the target coordinates (x, y) for which the cost is calculated.
        state (dict): The game state containing information about the current game situation.
        nearest_enemy (int): The index of the nearest enemy in the "enemies" list of the game state.

    Returns:
        float: The calculated normal cost for moving to the specified position without avoiding enemies.
    """
    total = 0

    if maze[position[0]][position[1]] == 1:
        total += POINTS_WALL
    else:
        total += 1

    for rock in state["rocks"]:
        rock_x, rock_y = rock["pos"]
        if (rock_x == position[0] and rock_y == position[1]) or (
            rock_x == position[0] and rock_y + 1 == position[1]
        ):
            total += POINTS_ROCKS

    for enemy in state["enemies"]:
        enemy_name = enemy["name"]
        enemy_x, enemy_y = enemy["pos"]

        if (
            "traverse" in enemy
            and enemy["traverse"] == True
            and calc_distance(position, enemy["pos"]) <= 5
        ):
            total += POINTS_GHOST

        if enemy_name == "Fygar":
            enemy_dir = enemy["dir"]
            if enemy_y == position[1]:
                # Vai bater com a cabeça na parede
                if enemy_x + 1 <= 47 and maze[enemy_x + 1][enemy_y] == 1:
                    if (
                        enemy_x == position[0]
                        or enemy_x - 1 == position[0]
                        or enemy_x - 2 == position[0]
                        or enemy_x - 3 == position[0]
                        or enemy_x - 4 == position[0]
                    ):
                        total += POINTS_FYGAR
                elif enemy_x - 1 >= 0 and maze[enemy_x - 1][enemy_y] == 1:
                    if (
                        enemy_x == position[0]
                        or enemy_x + 1 == position[0]
                        or enemy_x + 2 == position[0]
                        or enemy_x + 3 == position[0]
                        or enemy_x + 4 == position[0]
                    ):
                        total += POINTS_FYGAR
                else:
                    # Normal
                    if enemy_dir == 1:
                        if (
                            enemy_x == position[0]
                            or enemy_x + 1 == position[0]
                            or enemy_x + 2 == position[0]
                            or enemy_x + 3 == position[0]
                            or enemy_x + 4 == position[0]
                        ):
                            total += POINTS_FYGAR
                    elif enemy_dir == 3:
                        if (
                            enemy_x == position[0]
                            or enemy_x - 1 == position[0]
                            or enemy_x - 2 == position[0]
                            or enemy_x - 3 == position[0]
                            or enemy_x - 4 == position[0]
                        ):
                            total += POINTS_FYGAR

        cant_be_there = [
            (enemy_x, enemy_y),
            (enemy_x, enemy_y + 1),
            (enemy_x + 1, enemy_y),
            (enemy_x - 1, enemy_y),
            (enemy_x, enemy_y - 1),
        ]

        if position in cant_be_there:
            total += POINTS_POOKA

    return total


def calculate_cost_avoid_enemies(maze, position, state, nearest_enemy):
    """
    Calculates the cost of moving to a specific position while avoiding enemies.

    This function calculates the cost of moving to a specific position on the game map while considering
    the presence of rocks, ghosts, and other enemies. The cost is influenced by various factors, such as the
    proximity to rocks and ghosts, as well as penalties for avoiding enemies.

    Args:
        maze (list): A 2D list representing the game map where 1 indicates a wall and 0 indicates an open space.
        position (tuple): A tuple representing the target coordinates (x, y) for which the cost is calculated.
        state (dict): The game state containing information about the current game situation.
        nearest_enemy (int): The index of the nearest enemy in the "enemies" list of the game state.

    Returns:
        float: The calculated cost for moving to the specified position while avoiding enemies.
    """
    total = 0

    for rock in state["rocks"]:
        rock_x, rock_y = rock["pos"]
        if (rock_x == position[0] and rock_y == position[1]) or (
            rock_x == position[0] and rock_y + 1 == position[1]
        ):
            total += POINTS_ROCKS

    for enemy in state["enemies"]:
        enemy_name = enemy["name"]
        enemy_x, enemy_y = enemy["pos"]

        if (
            "traverse" in enemy
            and enemy["traverse"] == True
            and calc_distance(position, enemy["pos"]) <= 5
        ):
            total += POINTS_GHOST

        if enemy_name == "Fygar":
            enemy_dir = enemy["dir"]
            if enemy_y == position[1]:
                # Vai bater com a cabeça na parede
                if enemy_x + 1 <= 47 and maze[enemy_x + 1][enemy_y] == 1:
                    if (
                        enemy_x == position[0]
                        or enemy_x - 1 == position[0]
                        or enemy_x - 2 == position[0]
                        or enemy_x - 3 == position[0]
                        or enemy_x - 4 == position[0]
                    ):
                        total += POINTS_FYGAR
                elif enemy_x - 1 >= 0 and maze[enemy_x - 1][enemy_y] == 1:
                    if (
                        enemy_x == position[0]
                        or enemy_x + 1 == position[0]
                        or enemy_x + 2 == position[0]
                        or enemy_x + 3 == position[0]
                        or enemy_x + 4 == position[0]
                    ):
                        total += POINTS_FYGAR
                else:
                    # Normal
                    if enemy_dir == 1:
                        if (
                            enemy_x == position[0]
                            or enemy_x + 1 == position[0]
                            or enemy_x + 2 == position[0]
                            or enemy_x + 3 == position[0]
                            or enemy_x + 4 == position[0]
                        ):
                            total += POINTS_FYGAR
                    elif enemy_dir == 3:
                        if (
                            enemy_x == position[0]
                            or enemy_x - 1 == position[0]
                            or enemy_x - 2 == position[0]
                            or enemy_x - 3 == position[0]
                            or enemy_x - 4 == position[0]
                        ):
                            total += POINTS_FYGAR
        distance_to_enemy = abs(position[0] - enemy_x) + abs(position[1] - enemy_y)

        penalty = POINTS_AVOID / (distance_to_enemy + 1)

        total += penalty

        cant_be_there = [
            (enemy_x, enemy_y),
            (enemy_x, enemy_y + 1),
            (enemy_x + 1, enemy_y),
            (enemy_x - 1, enemy_y),
            (enemy_x, enemy_y - 1),
        ]
        if position in cant_be_there:
            total += POINTS_POOKA

    return total


def heuristic(a, b):
    """
    Calculates the Manhattan distance between two points in a 2D plane.

    This heuristic function computes the Manhattan distance between two points, which is the sum of the
    absolute differences of their x and y coordinates. It is commonly used in pathfinding algorithms to
    estimate the cost of reaching one point from another.

    Args:
        a (tuple): A tuple representing the coordinates (x, y) of the first point.
        b (tuple): A tuple representing the coordinates (x, y) of the second point.

    Returns:
        float: The Manhattan distance between the two points.
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(maze, start, state, nearest_enemy, last_move, moves_fygar, controlo=False):
    """
    Applies the A* algorithm to find the optimal path from the start to a goal position.

    This function implements the A* algorithm to calculate the optimal path from the start position to a goal.
    The goal position is determined based on the current game state, the nearest enemy, and additional parameters.

    Args:
        maze (list): A 2D list representing the game map where 1 indicates a wall and 0 indicates an open space.
        start (tuple): A tuple representing the starting coordinates (x, y) for the pathfinding.
        state (dict): The game state containing information about the current game situation.
        nearest_enemy (int): The index of the nearest enemy in the "enemies" list of the game state.
        last_move (str): The last move made by the player.
        moves_fygar (list): A list of previous moves made by the Fygar enemy.
        controlo (bool, optional): A flag indicating a specific control scenario. Defaults to False.

    Returns:
        str or None: A string representing the next move ('A' for shooting) or None if no valid move is found.
    """
    goal = (
        set_goal(state, nearest_enemy, maze, moves_fygar)
        if controlo == False
        else (0, 0)
    )
    digdug_x, digdug_y = start
    enemy_x, enemy_y = goal
    real_enemy_x, real_enemy_y = state["enemies"][nearest_enemy]["pos"]
    avoid = False

    if last_move is not None and can_shoot(
        state, maze, last_move, nearest_enemy, digdug_x, digdug_y
    ):
        return "A"
    elif (
        (
            (abs(digdug_x - real_enemy_x) <= 3 and digdug_y == real_enemy_y)
            or (abs(digdug_y - real_enemy_y) <= 3 and digdug_x == real_enemy_x)
            and can_shoot(state, maze, last_move, nearest_enemy, digdug_x, digdug_y)
            == False
        )
        or in_the_fire(state, maze, start)
        or in_the_fire(state, maze, goal)
        or controlo == True
    ):
        avoid = True
        if start == (0, 0):
            goal == (enemy_x, enemy_y)
        else:
            goal = (0, 0)

    if (
        int(state["step"]) > 2000
        and int(state["level"]) >= 8
        and len(state["enemies"]) < 4
    ):
        controlo = True

        for enemy in state["enemies"]:
            if enemy["name"] == "Fygar":
                controlo = False
                break

        if controlo:
            goal = (47, 23)

            if start == goal:
                return "A"

    priority_queue = [(0, start)]
    visited = set()
    came_from = {}
    cost_so_far = {start: 0}

    while priority_queue:
        current_cost, current_node = heapq.heappop(priority_queue)

        if current_node in visited:
            continue

        visited.add(current_node)

        if current_node == goal:
            path = reconstruct_path(start, goal, came_from)
            if avoid:
                return path

            # Ver o ultimo move
            if len(path) > 1:
                last_node = path[-2]
                dx, dy = current_node[0] - last_node[0], current_node[1] - last_node[1]

                if (
                    (
                        dx == 1 and real_enemy_x > digdug_x
                    )  # move para a direita e o inimigo esta a direita
                    or (
                        dx == -1 and real_enemy_x < digdug_x
                    )  # move para a esquerda e o inimigo esta a esquerda
                    or (
                        dy == 1 and real_enemy_y > digdug_y
                    )  # move para baixo e o inimigo esta abaixo
                    or (
                        dy == -1 and real_enemy_y < digdug_y
                    )  # move para cima e o inimigo esta acima
                ):
                    return path

                new_goal = None
                if real_enemy_x > digdug_x:
                    new_goal = (current_node[0] + 1, current_node[1])
                elif real_enemy_x < digdug_x:
                    new_goal = (current_node[0] - 1, current_node[1])
                elif real_enemy_y > digdug_y:
                    new_goal = (current_node[0], current_node[1] + 1)
                elif real_enemy_y < digdug_y:
                    new_goal = (current_node[0], current_node[1] - 1)

                if new_goal is not None:
                    # print("new goal")
                    path[-1] = new_goal

                return path

        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx_, ny_ = current_node[0] + dx, current_node[1] + dy
            if 0 <= nx_ < len(maze) and 0 <= ny_ < len(maze[0]):
                neighbor = (nx_, ny_)

                control = False
                for enemy in state["enemies"]:
                    if (
                        current_node[0] != 0
                        and current_node[0] != 47
                        and current_node[1] != 0
                        and current_node[1] != 23
                    ):
                        """if enemy["name"] == "Fygar":
                        if goal != neighbor and in_the_fire(state, maze, neighbor):
                            control = True
                            break"""
                        if enemy["name"] != "Fygar":
                            if (
                                abs(nx_ - enemy["pos"][0]) <= 1
                                and abs(ny_ - enemy["pos"][1]) <= 1
                            ):
                                control = True
                                break

                """ for rock in state["rocks"]:
                    rock_x, rock_y = rock["pos"]
                    if [rock_x, rock_y] == [nx_, ny_] or [rock_x, rock_y + 1] == [
                        nx_,
                        ny_,
                    ]:
                        control = True
                        break """

                if control:
                    continue

                new_cost = cost_so_far[current_node] + (
                    calculate_cost_avoid_enemies(maze, neighbor, state, nearest_enemy)
                    if avoid
                    else calculate_cost_normal(maze, neighbor, state, nearest_enemy)
                )

                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    came_from[neighbor] = current_node
                    total_cost = new_cost + heuristic(neighbor, goal)
                    heapq.heappush(priority_queue, (total_cost, neighbor))

    return None


def reconstruct_path(start, goal, came_from):
    """
    Reconstructs the path from the start to the goal using the came_from dictionary.

    This function reconstructs the path from the start position to the goal position based on the
    information stored in the came_from dictionary, which represents the predecessors of each node in the path.

    Args:
        start (tuple): A tuple representing the starting coordinates (x, y) for the pathfinding.
        goal (tuple): A tuple representing the goal coordinates (x, y) for the pathfinding.
        came_from (dict): A dictionary where keys are nodes in the path, and values are their predecessors.

    Returns:
        list: A list representing the ordered sequence of nodes from the start to the goal.
    """
    current = goal
    path = [current]
    while current != start:
        current = came_from[current]
        path.append(current)
    return path[::-1]
