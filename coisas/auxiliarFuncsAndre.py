linhas = 24
colunas = 48


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
    """
    Set the goal position for a specific enemy based on the current game state.

    Args:
        state (dict): The current game state containing information about the enemies, player, level, etc.
        enemy (int): The index of the enemy for which the goal position is being set.
        mapa (list): The game map.
        moves_fygar (dict): A dictionary storing the move history of Fygar enemies.

    Returns:
        tuple: A tuple containing the x and y coordinates representing the goal position for the enemy.

    This function determines the goal position for a specific enemy based on various factors such as
    the enemy's current direction, position, and the game map. The goal is adjusted to avoid obstacles
    and handle specific scenarios for certain enemy types.

    Note:
        The function may modify the enemy's x and y coordinates based on the defined conditions.

    Example:
        set_goal(state, 0, mapa, moves_fygar)
    """

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
