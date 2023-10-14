from collections import deque
from student import mapa

class Node:
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action

def bfs(initial_state):
    # No bfs basicamente definimos um estado inicial e depois vamos gerando estados filhos até encontrarmos o estado final
    # Por exemplo no nosso caso o estado inicial é o estado do jogo no inicio e o estado final é quando ja matamos os bichos todos
    # Vamos vendo os estados filhos e as ações possiveis até matarmos os bicharoucos todos

    queue = deque()
    visited = set()
    
    root = Node(initial_state)
    queue.append(root)

    while queue:
        node = queue.popleft()
        current_state = node.state
        
        # Primeiro verificamos se o estado atual é o estado final, ou seja se o gajo ja matou os bichos todos
        if is_winning_state(current_state):
            # Se for o estado final vamos buscar as ações que o gajo tomou para chegar a esse estado
            moves = []
            while node.parent:
                moves.append(node.action)
                node = node.parent
            moves.reverse() # Aqui temos de inverter a lista porque o gajo vai buscar as ações ao contrario
            return moves
        
        # Se não for o estado final vamos ver os estados filhos
        for action in possible_actions(current_state):
            next_state = simulate_action(current_state, action)
            if next_state not in visited:
                child_node = Node(next_state, node, action)
                queue.append(child_node)
                visited.add(next_state)

    return None

# Implementem para aqui as funções auxiliares que precisarem para testar a situação atual e gerar os estados filhos

def is_winning_state(game_state):
    # O nosso estado final é quando ja matamos os bichos todos por isso quando o tamanho da lista de inimigos for 0
    enemies = game_state['enemies']
    return len(enemies) == 0

def possible_actions(game_state):
    # Determine valid actions based on the current game state.
    # For Dig Dug, valid actions might include moving up, down, left, right, and shooting.
    # Ensure actions are within the game boundaries and don't lead to collisions with obstacles.
    # Add valid actions to the 'actions' list.

    actions = []
    digdug_x, digdug_y = game_state['digdug']

    if can_move(game_state, digdug_x - 1, digdug_y):
        actions.append('w')
    if can_move(game_state, digdug_x + 1, digdug_y):
        actions.append('s')
    if can_move(game_state, digdug_x, digdug_y - 1):
        actions.append('a')
    if can_move(game_state, digdug_x, digdug_y + 1):
        actions.append('d')
    actions.append(' ')
    return actions

def simulate_action(game_state, action):
    # Simulate the effect of taking an action on the current game state.
    # This function should return a new game state after the action is taken.
    # Make sure to update the positions of Dig Dug, enemies, and any other relevant game elements.
    new_game_state = game_state.copy()
    digdug_x, digdug_y = new_game_state['digdug']

    if action == 'w':
        if can_move(new_game_state, digdug_x - 1, digdug_y):
            new_game_state['digdug'] = [digdug_x - 1, digdug_y]
    elif action == 's':
        if can_move(new_game_state, digdug_x + 1, digdug_y):
            new_game_state['digdug'] = [digdug_x + 1, digdug_y]
    elif action == 'a':
        if can_move(new_game_state, digdug_x, digdug_y - 1):
            new_game_state['digdug'] = [digdug_x, digdug_y - 1]
    elif action == 'd':
        if can_move(new_game_state, digdug_x, digdug_y + 1):
            new_game_state['digdug'] = [digdug_x, digdug_y + 1]
    elif action == ' ':
        pass
    elif action == 'A': # disparar
        pass

    return new_game_state

def can_move(game_state, x, y):
    # Implemente a lógica para verificar se é possível mover-se para a posição (x, y) sem colidir com obstáculos ou inimigos.
    # Retorne True se for possível, False caso contrário.
    # Considere a representação do mapa no seu código para verificar colisões.
    if x < 0 or x >= len(mapa) or y < 0 or y >= len(mapa[0]):
        return False
    return mapa[x][y] == 0
