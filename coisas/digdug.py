import math
from tree_search import *


class DigDug:
    def __init__(self, connections, coordinates):
        self.connections = connections
        self.coordinates = coordinates

    def actions(self, city):
        actlist = []
        for C1, C2, D in self.connections:
            if C1 == city:
                actlist += [(C1, C2)]
            elif C2 == city:
                actlist += [(C2, C1)]
        return actlist

    def result(self, city, action):
        (C1, C2) = action
        if C1 == city:
            return C2

    def cost(self, city, action):
        a1, a2 = action
        assert a1 == city

        for c1, c2, c in self.connections:
            if (c1, c2) in [(a1, a2), (a2, a1)]:
                return c

    def heuristic(self, city, goal_city):
        return math.dist(self.coordinates[city], self.coordinates[goal_city])

    def satisfies(self, city, goal_city):
        return goal_city == city
