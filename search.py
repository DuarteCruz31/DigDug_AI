import sys


class Graph(object):
    def __init__(self, nodes, init_graph):
        self.nodes = nodes
        self.graph = self.construct_graph(nodes, init_graph)

    def construct_graph(self, nodes, init_graph):
        """
        This method makes sure that the graph is symmetrical. In other words, if there's a path from node A to B with a value V, there needs to be a path from node B to node A with a value V.
        """
        graph = {}
        for node in nodes:
            graph[node] = {}

        graph.update(init_graph)

        for node, edges in graph.items():
            for adjacent_node, value in edges.items():
                if graph[adjacent_node].get(node, False) == False:
                    graph[adjacent_node][node] = value

        return graph

    def get_nodes(self):
        "Returns the nodes of the graph."
        return self.nodes

    def get_outgoing_edges(self, node):
        "Returns the neighbors of a node."
        connections = []
        for out_node in self.nodes:
            if self.graph[node].get(out_node, False) != False:
                connections.append(out_node)
        return connections

    def value(self, node1, node2):
        "Returns the value of an edge between two nodes."
        return self.graph[node1][node2]


def dijkstra_algorithm(graph, start_node):
    unvisited_nodes = list(graph.get_nodes())

    # We'll use this dict to save the cost of visiting each node and update it as we move along the graph
    shortest_path = {}

    # We'll use this dict to save the shortest known path to a node found so far
    previous_nodes = {}

    # We'll initialize the cost of visiting each node with infinity
    for node in unvisited_nodes:
        shortest_path[node] = sys.maxsize

    # We'll set the cost of visiting the start node to 0
    shortest_path[start_node] = 0

    while len(unvisited_nodes) > 0:
        # We'll get the unvisited node with the lowest cost
        current_node = None
        for node in unvisited_nodes:
            if current_node == None:
                current_node = node
            elif shortest_path[node] < shortest_path[current_node]:
                current_node = node

        # We'll get the neighbors of the current node
        neighbors = graph.get_outgoing_edges(current_node)

        # We'll calculate the cost of visiting each neighbor
        for neighbor in neighbors:
            cost = graph.value(current_node, neighbor) + shortest_path[current_node]

            # If the cost is lower than the previously known cost, we'll update the cost and the shortest path
            if cost < shortest_path[neighbor]:
                shortest_path[neighbor] = cost
                previous_nodes[neighbor] = current_node

        # We'll remove the current node from the list of unvisited nodes
        unvisited_nodes.remove(current_node)

    return previous_nodes


def print_result(previous_nodes, start_node, target_node):
    path = []
    node = target_node

    # print(previous_nodes)

    while node != start_node:
        path.append(node)
        if node not in previous_nodes:
            return None
        node = previous_nodes[node]

    path = ["(" + str(tuple[0]) + ", " + str(tuple[1]) + ")" for tuple in path]

    path.append("(" + str(start_node[0]) + ", " + str(start_node[1]) + ")")

    return path


def shortest_path(graph, node1, node2):
    path_list = [[node1]]
    path_index = 0
    # To keep track of previously visited nodes
    previous_nodes = {node1}
    if node1 == node2:
        return path_list[0]

    while path_index < len(path_list):
        current_path = path_list[path_index]
        last_node = current_path[-1]
        next_nodes = graph[last_node]
        # Search goal node
        if node2 in next_nodes:
            current_path.append(node2)
            return current_path
        # Add new paths
        for next_node in next_nodes:
            if not next_node in previous_nodes:
                new_path = current_path[:]
                new_path.append(next_node)
                path_list.append(new_path)
                # To avoid backtracking
                previous_nodes.add(next_node)
        # Continue to next path in list
        path_index += 1
    # No path is found
    return []
