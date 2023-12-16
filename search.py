import heapq

linhas = 24
colunas = 48

POINTS_ROCKS = 10000
POINTS_FYGAR = 10000
POINTS_WALL = 5
POINTS_POOKA = 10000
POINTS_GHOST = 10000
POINTS_AVOID = 10000


def calc_distance(position, end):
    """
    Calculates the distance between two positions in a 2D plane.

    This function uses the Manhattan distance metric, which is the sum of the absolute differences
    of the x and y coordinates between the initial and final positions.

    Args:
        position (tuple): A tuple representing the coordinates (x, y) of the initial position.
        end (tuple): A tuple representing the coordinates (x, y) of the final position.

    Returns:
        int: The Manhattan distance between the two positions.
    """
    return abs((position[0] - end[0])) + abs((position[1] - end[1]))


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


def enemies_not_in_the_same_position(state, nearest_enemy):
    """
    Checks if the nearest enemy is not in the same position as any other enemy.

    This function examines the positions of the nearest enemy and other enemies and determines
    if the nearest enemy is not in the same position as any other enemy.

    Args:
        state (dict): The game state containing information about the current game situation.
        nearest_enemy (int): The index of the nearest enemy in the "enemies" list of the game state.

    Returns:
        bool: True if the nearest enemy is not in the same position as any other enemy, False otherwise.
    """
    for enemy in state["enemies"]:
        if enemy != state["enemies"][nearest_enemy]:
            if enemy["pos"] == state["enemies"][nearest_enemy]["pos"]:
                return False
    return True


def not_sandwiched(state, mapa, nearest_enemy, digdug_x, digdug_y):
    """
    Checks if Dig Dug is not sandwiched between the nearest enemy and another enemy.

    This function examines the positions of Dig Dug, the nearest enemy, and other enemies, and
    determines if Dig Dug is not sandwiched between the nearest enemy and another enemy.

    Args:
        state (dict): The game state containing information about the current game situation.
        mapa (list): A 2D list representing the game map where 1 indicates a wall and 0 indicates an open space.
        nearest_enemy (int): The index of the nearest enemy in the "enemies" list of the game state.
        digdug_x (int): The x-coordinate of Dig Dug's current position.
        digdug_y (int): The y-coordinate of Dig Dug's current position.

    Returns:
        bool: True if Dig Dug is not sandwiched between the nearest enemy and another enemy, False otherwise.
    """
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


def check_other_enimies_while_shooting(state, mapa, nearest_enemy):
    """
    Checks if other enemies are in the line of fire while Dig Dug is shooting.

    This function examines the positions of other enemies relative to Dig Dug's shooting direction
    and determines if they are in the line of fire while Dig Dug is shooting.

    Args:
        state (dict): The game state containing information about the current game situation.
        mapa (list): A 2D list representing the game map where 1 indicates a wall and 0 indicates an open space.
        nearest_enemy (int): The index of the nearest enemy in the "enemies" list of the game state.

    Returns:
        bool: True if no other enemies are in the line of fire while Dig Dug is shooting, False otherwise.
    """
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


def can_shoot(state, mapa, last_move, nearest_enemy, digdug_x, digdug_y):
    """
    Checks if the player can shoot at the nearest enemy based on the current game state.

    This function examines the game state, the player's last move, and the position of the nearest enemy
    to determine if the player can shoot at the enemy.

    Args:
        state (dict): The game state containing information about the current game situation.
        mapa (list): A 2D list representing the game map where 1 indicates a wall and 0 indicates an open space.
        last_move (str): The last move made by the player.
        nearest_enemy (int): The index of the nearest enemy in the "enemies" list of the game state.
        digdug_x (int): The x-coordinate of Dig Dug's current position.
        digdug_y (int): The y-coordinate of Dig Dug's current position.

    Returns:
        bool: True if the player can shoot at the nearest enemy, False otherwise.
    """
    shooting_distance = 3
    enemy_x, enemy_y = state["enemies"][nearest_enemy]["pos"]

    # Check if the player can shoot based on the last move and relative positions of Dig Dug and the nearest enemy.
    if last_move == "d":
        # Check if the enemy is to the right and within shooting distance.
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
    elif last_move == "a":
        # Check if the enemy is to the left and within shooting distance.
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
    elif last_move == "w":
        # Check if the enemy is above and within shooting distance.
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
    elif last_move == "s":
        # Check if the enemy is below and within shooting distance.
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
    elif last_move == "A":
        # Check if the player is currently shooting and can hit the enemy.
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


def in_the_fire(state, maze, position):
    """
    Checks if the player is in danger of being attacked by Fygar enemies in the current game state.

    This function examines the positions of Fygar enemies and determines if the player is in danger
    of being attacked based on the Fygar's current direction and the proximity to the player.

    Args:
        state (dict): The game state containing information about the current game situation.
        maze (list): A 2D list representing the game maze where 1 indicates a wall and 0 indicates an open space.
        position (tuple): A tuple representing the player's current position (x, y).

    Returns:
        bool: True if the player is in danger of being attacked by Fygar enemies, False otherwise.
    """
    for enemy in state["enemies"]:
        enemy_name = enemy["name"]
        enemy_x, enemy_y = enemy["pos"]

        if enemy_name == "Fygar":
            enemy_dir = enemy["dir"]

            # Check if the Fygar is in a position to attack the player.
            if enemy_y == position[1]:
                if enemy_x + 1 <= 47 and maze[enemy_x + 1][enemy_y] == 1:
                    if (
                        enemy_x == position[0]
                        or enemy_x - 1 == position[0]
                        or enemy_x - 2 == position[0]
                        or enemy_x - 3 == position[0]
                        or enemy_x - 4 == position[0]
                    ):
                        return True
                elif enemy_x - 1 >= 0 and maze[enemy_x - 1][enemy_y] == 1:
                    if (
                        enemy_x == position[0]
                        or enemy_x + 1 == position[0]
                        or enemy_x + 2 == position[0]
                        or enemy_x + 3 == position[0]
                        or enemy_x + 4 == position[0]
                    ):
                        return True
                else:
                    # Normal movement
                    if enemy_dir == 1:
                        if (
                            enemy_x == position[0]
                            or enemy_x + 1 == position[0]
                            or enemy_x + 2 == position[0]
                            or enemy_x + 3 == position[0]
                            or enemy_x + 4 == position[0]
                        ):
                            return True
                    elif enemy_dir == 3:
                        if (
                            enemy_x == position[0]
                            or enemy_x - 1 == position[0]
                            or enemy_x - 2 == position[0]
                            or enemy_x - 3 == position[0]
                            or enemy_x - 4 == position[0]
                        ):
                            return True
    return False


def fygar_is_repeating_positions(moves_fygar):
    """
    Checks if the Fygar enemy has repeated its positions in the last 10 moves.

    This function examines the last 10 moves made by the Fygar enemy and determines if it has
    repeated its position in a pattern.

    Args:
        moves_fygar (list): A list containing the recent moves made by the Fygar enemy.

    Returns:
        bool: True if the Fygar enemy has repeated its positions in a specific pattern in the last 10 moves, False otherwise.
    """
    # Ensure there are at least 10 moves to check.
    if len(moves_fygar) < 10:
        return False

    # Check if the Fygar has repeated its positions in a specific pattern.
    if (
        moves_fygar[-1] == moves_fygar[-3]
        and moves_fygar[-2] == moves_fygar[-4]
        and moves_fygar[-1] == moves_fygar[-5]
        and moves_fygar[-2] == moves_fygar[-6]
        and moves_fygar[-1] == moves_fygar[-7]
        and moves_fygar[-2] == moves_fygar[-8]
    ):
        return True

    return False


def nearest_fygar_stuck_on_rock(state, mapa, nearest_enemy):
    """
    Checks if the nearest Fygar enemy is stuck on a rock based on the game state and map.

    This function determines if the enemy is surrounded by walls/rocks in all four adjacent positions
    (top, bottom, left, and right).

    Args:
        state (dict): The game state containing information about the current game situation.
        mapa (list): A 2D list representing the game map where 1 indicates a wall/rock and 0 indicates empty space.
        nearest_enemy (int): The index of the nearest Fygar enemy in the "enemies" list of the game state.

    Returns:
        bool: True if the nearest Fygar enemy is stuck on a rock, False otherwise.
    """
    enemy_x, enemy_y = state["enemies"][nearest_enemy]["pos"]

    # Check if the enemy is surrounded by rocks in all four adjacent positions.
    if (
        enemy_x + 1 <= 47
        and enemy_x - 1 >= 0
        and enemy_y + 1 <= 23
        and enemy_y - 1 >= 0
        and mapa[enemy_x + 1][enemy_y] == 1
        and mapa[enemy_x - 1][enemy_y] == 1
        and mapa[enemy_x][enemy_y + 1] == 1
        and mapa[enemy_x][enemy_y - 1] == 1
    ):
        return True
    return False


def set_goal(state, enemy, mapa, moves_fygar):
    enemy_x, enemy_y = state["enemies"][enemy]["pos"]
    digdug_x, digdug_y = state["digdug"]
    enemy_dir = state["enemies"][enemy]["dir"]
    enemy_name = state["enemies"][enemy]["name"]
    level = int(state["level"])
    id = state["enemies"][enemy]["id"]

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
    else:
        if enemy_dir == 0 and enemy_y + 2 <= linhas - 1:  # cima
            enemy_y += 2
        elif enemy_dir == 1 and enemy_x - 2 >= 0:  # direita
            enemy_x -= 2
        elif enemy_dir == 2 and enemy_y - 2 >= 0:  # baixo
            enemy_y -= 2
        elif enemy_dir == 3 and enemy_x + 2 <= colunas - 1:  # esquerda
            enemy_x += 2

    """ if level >= 7 and enemy_name == "Fygar":
        enemy_x, enemy_y = state["enemies"][enemy]["pos"] """

    if level >= 7 and id in moves_fygar:
        if fygar_is_repeating_positions(moves_fygar[id]):
            # print("repetiu")
            previous_move = moves_fygar[id][
                -1
            ]  # (x, y)  (23,12) -> (22, 12) -> (23,12)
            second_move = moves_fygar[id][-2]  # (x, y)   (23,12) -> (23,13) -> (23,12)

            if previous_move[0] == second_move[0]:
                if previous_move[1] > second_move[1]:
                    enemy_x = previous_move[0]
                    enemy_y = (
                        previous_move[1] + 1 if int(previous_move[1]) + 1 < 23 else -1
                    )
                elif previous_move[1] < second_move[1]:
                    enemy_x = second_move[0]
                    enemy_y = second_move[1] + 1 if int(second_move[1]) + 1 < 23 else -1
            elif previous_move[1] == second_move[1]:
                if previous_move[0] > second_move[0]:
                    enemy_x = previous_move[0]
                    enemy_y = (
                        previous_move[1] + 1 if int(previous_move[1]) + 1 < 23 else -1
                    )
                elif previous_move[0] < second_move[0]:
                    enemy_x = second_move[0]
                    enemy_y = (
                        previous_move[1] + 1 if int(previous_move[1]) + 1 < 23 else -1
                    )

    if enemy_name == "Fygar" and nearest_fygar_stuck_on_rock(state, mapa, enemy):
        enemy_x, enemy_y = state["enemies"][enemy]["pos"]
        enemy_y += 1

    return (enemy_x, enemy_y)


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
