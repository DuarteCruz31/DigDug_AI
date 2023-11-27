class Node:
    def __init__(self, parent=None, position=None, steps=None):
        self.parent = parent
        self.position = position
        self.steps = steps if steps is not None else []

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position


linhas = 24
colunas = 48

POINTS_ROCKS = 1000
POINTS_FYGAR = 300
POINTS_WALL = 100
POINTS_POOKA = 300
POINTS_GHOST = 1000


def calc_distance(position, end):
    return abs((position[0] - end[0])) + abs((position[1] - end[1]))


def calculate_cost_normal(maze, position, state, nearest_enemy):
    total = 0
    enemy_x, enemy_y = state["enemies"][nearest_enemy]["pos"]
    cant_be_there = [
        (enemy_x, enemy_y),
        (enemy_x, enemy_y + 1),
        (enemy_x + 1, enemy_y),
        (enemy_x - 1, enemy_y),
        (enemy_x, enemy_y - 1),
    ]

    if maze[position[0]][position[1]] == 1:
        total += POINTS_WALL

    if (
        "traverse" in state["enemies"][nearest_enemy]
        and state["enemies"][nearest_enemy]["traverse"] == True
        and calc_distance(state["digdug"], state["enemies"][nearest_enemy]["pos"]) <= 5
    ):
        if position in cant_be_there:
            total += POINTS_GHOST

    for rock in state["rocks"]:
        rock_x, rock_y = rock["pos"]
        if rock_x == position[0] and rock_y == position[1]:
            total += POINTS_ROCKS

    for enemy in state["enemies"]:
        enemy_name = enemy["name"]
        enemy_x, enemy_y = enemy["pos"]
        if enemy_name == "Fygar":
            enemy_dir = enemy["dir"]
            if enemy_y == position[1]:
                if enemy_dir == 1 and enemy_x + 4 <= 48 and enemy_x - 4 >= 0:
                    if maze[enemy_x + 1][enemy_y] == 1 and (
                        enemy_x == position[0]
                        or enemy_x - 1 == position[0]
                        or enemy_x - 2 == position[0]
                        or enemy_x - 3 == position[0]
                        or enemy_x - 4 == position[0]
                    ):
                        total += POINTS_FYGAR
                    elif (
                        enemy_x == position[0]
                        or enemy_x + 1 == position[0]
                        or enemy_x + 2 == position[0]
                        or enemy_x + 3 == position[0]
                        or enemy_x + 4 == position[0]
                    ):
                        total += POINTS_FYGAR
                elif enemy_dir == 3 and enemy_x - 4 >= 0 and enemy_x + 4 <= 48:
                    if maze[enemy_x - 1][enemy_y] == 1 and (
                        enemy_x == position[0]
                        or enemy_x + 1 == position[0]
                        or enemy_x + 2 == position[0]
                        or enemy_x + 3 == position[0]
                        or enemy_x + 4 == position[0]
                    ):
                        total += POINTS_FYGAR
                    elif (
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
    total = 0
    enemy_x, enemy_y = state["enemies"][nearest_enemy]["pos"]
    cant_be_there = [
        (enemy_x, enemy_y),
        (enemy_x, enemy_y + 1),
        (enemy_x + 1, enemy_y),
        (enemy_x - 1, enemy_y),
        (enemy_x, enemy_y - 1),
    ]

    if maze[position[0]][position[1]] == 1:
        total += POINTS_WALL

    if (
        "traverse" in state["enemies"][nearest_enemy]
        and state["enemies"][nearest_enemy]["traverse"] == True
        and calc_distance(state["digdug"], state["enemies"][nearest_enemy]["pos"]) <= 5
    ):
        if position in cant_be_there:
            total += POINTS_GHOST

    for rock in state["rocks"]:
        rock_x, rock_y = rock["pos"]
        if rock_x == position[0] and rock_y == position[1]:
            total += POINTS_ROCKS

    for enemy in state["enemies"]:
        enemy_name = enemy["name"]
        enemy_x, enemy_y = enemy["pos"]
        enemy_dir = enemy["dir"]

        if enemy_name == "Fygar":
            if enemy_y == position[1]:
                if enemy_dir == 1 and enemy_x + 4 <= 48 and enemy_x - 4 >= 0:
                    if maze[enemy_x + 1][enemy_y] == 1 and (
                        enemy_x == position[0]
                        or enemy_x - 1 == position[0]
                        or enemy_x - 2 == position[0]
                        or enemy_x - 3 == position[0]
                        or enemy_x - 4 == position[0]
                    ):
                        total += POINTS_FYGAR
                    elif (
                        enemy_x == position[0]
                        or enemy_x + 1 == position[0]
                        or enemy_x + 2 == position[0]
                        or enemy_x + 3 == position[0]
                        or enemy_x + 4 == position[0]
                    ):
                        total += POINTS_FYGAR
                elif enemy_dir == 3 and enemy_x - 4 >= 0 and enemy_x + 4 <= 48:
                    if maze[enemy_x - 1][enemy_y] == 1 and (
                        enemy_x == position[0]
                        or enemy_x + 1 == position[0]
                        or enemy_x + 2 == position[0]
                        or enemy_x + 3 == position[0]
                        or enemy_x + 4 == position[0]
                    ):
                        total += POINTS_FYGAR
                    elif (
                        enemy_x == position[0]
                        or enemy_x - 1 == position[0]
                        or enemy_x - 2 == position[0]
                        or enemy_x - 3 == position[0]
                        or enemy_x - 4 == position[0]
                    ):
                        total += POINTS_FYGAR

        distance_to_enemy = (
            abs(position[0] - enemy_x) ** 2 + abs(position[1] - enemy_y) ** 2
        )

        penalty = 300 / (distance_to_enemy + 1)

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


""" def calc_distance(position, end):
    return (((position[0] - end[0]) ** 2) + ((position[1] - end[1]) ** 2)) ** 0.5 """


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


def astar(maze, start, end, state, nearest_enemy, last_move):
    digdug_x, digdug_y = start
    enemy_x, enemy_y = end
    avoid = False

    if last_move != None and can_shoot(state, maze, last_move, nearest_enemy):
        return "A"
    elif (abs(digdug_x - enemy_x) < 3 and digdug_y == enemy_y) or (
        abs(digdug_y - enemy_y) < 3 and digdug_x == enemy_x
    ):
        avoid = True

    start_node = Node(None, start)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, end)
    end_node.g = end_node.h = end_node.f = 0

    open_list = []
    closed_list = []

    open_list.append(start_node)

    while len(open_list) > 0:
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        open_list.pop(current_index)
        closed_list.append(current_node)

        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1]

        children = []
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            node_position = (
                current_node.position[0] + new_position[0],
                current_node.position[1] + new_position[1],
            )

            if (
                node_position[0] > (len(maze) - 1)
                or node_position[0] < 0
                or node_position[1] > (len(maze[len(maze) - 1]) - 1)
                or node_position[1] < 0
            ):
                continue

            new_node = Node(
                current_node, node_position, current_node.steps + [node_position]
            )

            children.append(new_node)

        for child in children:
            if child in closed_list:
                continue

            if avoid:
                child.g = current_node.g + calculate_cost_avoid_enemies(
                    maze, child.position, state, nearest_enemy
                )
            else:
                child.g = current_node.g + calculate_cost_normal(
                    maze, child.position, state, nearest_enemy
                )

            child.h = (child.position[0] - end_node.position[0]) ** 2 + (
                (child.position[1] - end_node.position[1]) ** 2
            )

            child.f = child.g + child.h

            if child not in open_list or child.g < open_list[open_list.index(child)].g:
                open_list.append(child)

    return None
