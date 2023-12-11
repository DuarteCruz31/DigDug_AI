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
    return abs((position[0] - end[0])) + abs((position[1] - end[1]))


def calculate_cost_normal(maze, position, state, nearest_enemy):
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
    total = 0

    if maze[position[0]][position[1]] == 0:
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


def can_shoot(state, mapa, last_move, nearest_enemy, digdug_x, digdug_y):
    # print(last_move)
    shooting_distance = 3
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


def heuristic(a, b):
    # distancia euclidiana, faz com nao ande na diagonal
    # disancia de manhattan, faz com que ande na diagonal
    # distancia de chebyshev ou o caralhs, faz com que ande na diagonal
    # return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def in_the_fire(state, maze, position):
    for enemy in state["enemies"]:
        enemy_name = enemy["name"]
        enemy_x, enemy_y = enemy["pos"]
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
                        return True
                elif enemy_x - 1 >= 0 and maze[enemy_x + 1][enemy_y] == 1:
                    if (
                        enemy_x == position[0]
                        or enemy_x + 1 == position[0]
                        or enemy_x + 2 == position[0]
                        or enemy_x + 3 == position[0]
                        or enemy_x + 4 == position[0]
                    ):
                        return True
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


def nearest_is_fygar_bugged(f, id):
    if id in f:
        return f[id].has_repeated_values()
    return False


def nearest_is_rock_bugged(maze, enemy, digdug, t):
    if (
        enemy[0] != 47
        and enemy[1] != 23
        and t == False
        and maze[enemy[0]][enemy[1] + 1] >= 0
        and maze[enemy[0]][enemy[1] - 1] >= 0
        and maze[enemy[0] + 1][enemy[1]] >= 0
        and maze[enemy[0] - 1][enemy[1]] >= 0
        and (
            maze[enemy[0]][enemy[1] + 1] == 1 and maze[enemy[0]][enemy[1] + 1] != digdug
        )
        and (
            maze[enemy[0]][enemy[1] - 1] == 1 and maze[enemy[0]][enemy[1] + 1] != digdug
        )
        and (
            maze[enemy[0] + 1][enemy[1]] == 1 and maze[enemy[0]][enemy[1] + 1] != digdug
        )
        and (
            maze[enemy[0] - 1][enemy[1]] == 1 and maze[enemy[0]][enemy[1] + 1] != digdug
        )
    ):
        return True
    return False


def astar(maze, start, goal, state, nearest_enemy, last_move, fygars):
    digdug_x, digdug_y = start
    enemy_x, enemy_y = goal
    real_enemy_x, real_enemy_y = state["enemies"][nearest_enemy]["pos"]
    avoid = False

    if last_move is not None and can_shoot(
        state, maze, last_move, nearest_enemy, digdug_x, digdug_y
    ):
        return "A"
    elif (
        (abs(digdug_x - real_enemy_x) <= 3 and digdug_y == real_enemy_y)
        or (abs(digdug_y - real_enemy_y) <= 3 and digdug_x == real_enemy_x)
        and can_shoot(state, maze, last_move, nearest_enemy, digdug_x, digdug_y)
        == False
    ) or in_the_fire(state, maze, start):
        avoid = True
        if start == (0, 0):
            goal == (enemy_x, enemy_y)
        else:
            goal = (0, 0)
    elif nearest_is_fygar_bugged(fygars, state["enemies"][nearest_enemy]["name"]):
        print("nearest_is_fygar_bugged")
    elif nearest_is_rock_bugged(
        maze,
        state["enemies"][nearest_enemy]["pos"],
        [digdug_x, digdug_y],
        "traverse" in state["enemies"][nearest_enemy],
    ):
        print("nearest_is_rock_bugged")

    if int(state["step"]) > 2000:
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
            last_node = path[-2]
            dx, dy = current_node[0] - last_node[0], current_node[1] - last_node[1]

            if (
                (dx == 1 and real_enemy_x > digdug_x)
                or (dx == -1 and real_enemy_x < digdug_x)
                or (dy == 1 and real_enemy_y > digdug_y)
                or (dy == -1 and real_enemy_y < digdug_y)
            ):
                return path

            # Se o último movimento não estiver na direção do inimigo, remove o último nó e adiciona um novo ja bem
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

                if (
                    state["enemies"][nearest_enemy]["name"] == "Fygar"
                    and int(state["level"]) >= 7
                ):
                    if goal != neighbor and in_the_fire(state, maze, neighbor):
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
    current = goal
    path = [current]
    while current != start:
        current = came_from[current]
        path.append(current)
    return path[::-1]
