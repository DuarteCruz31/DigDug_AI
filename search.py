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


def calculate_cost(maze, position):
    return 2 if maze[position[0]][position[1]] == 1 else 0


def in_the_fire(state, position):
    for enemy in state["enemies"]:
        enemy_name = enemy["name"]
        if enemy_name == "Fygar":
            enemy_x, enemy_y = enemy["pos"]
            enemy_dir = enemy["dir"]
            if enemy_y == position[1]:
                if (
                    enemy_dir == 1
                    and enemy_x + 4 <= 48
                    and (
                        enemy_x == position[0]
                        or enemy_x + 1 == position[0]
                        or enemy_x + 2 == position[0]
                        or enemy_x + 3 == position[0]
                        or enemy_x + 4 == position[0]
                    )
                ):
                    return 2
                elif (
                    enemy_dir == 3
                    and enemy_x - 4 >= 0
                    and (
                        enemy_x == position[0]
                        or enemy_x - 1 == position[0]
                        or enemy_x - 2 == position[0]
                        or enemy_x - 3 == position[0]
                        or enemy_x - 4 == position[0]
                    )
                ):
                    return 2
    return 0


def astar(maze, start, end, state):
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

            child.g = current_node.g + calculate_cost(maze, child.position)

            child.h = (
                ((child.position[0] - end_node.position[0]) ** 2)
                + ((child.position[1] - end_node.position[1]) ** 2)
                + 5 * in_the_fire(state, child.position)
            )

            child.f = child.g + child.h

            if child not in open_list or child.g < open_list[open_list.index(child)].g:
                open_list.append(child)

    return None
