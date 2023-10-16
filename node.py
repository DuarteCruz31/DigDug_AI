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
    actions.append('A')
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

def is_moving(enemy_state,mapa):
    #se ele se estiver a mexer entre tuneis
    #return true se ele se estiver a mexer e false se estiver num tunel previamente cavado
    if mapa[enemy_state[0],enemy_state[1]] == 0:
        return True
    return False
    
def tunnels(game_state1):
    tuneis = []
    for enemy in game_state1['enemies']:
        enemyx, enemyy = enemy['pos']
        direction = enemy['dir']        
        tunel = []


        if direction == 0:
            for x in range(9):
                tunel.append([enemyx,enemyy-x])
            tuneis.append(tunel)
        elif direction == 1:
            for x in range(9):
                tunel.append([enemyx+x,enemyy])
            tuneis.append(tunel)
        elif direction == 2:
            for x in range(9):
                tunel.append([enemyx,enemyy+x])
            tuneis.append(tunel)
        elif direction == 3:
            for x in range(9):
                tunel.append([enemyx-x,enemyy])
            tuneis.append(tunel)
        else:
            print("ERRO CARALHO")

    return tuneis

def can_calculate(f_state,l_state):
    pos = []
    pos2 = []
    for enemy in f_state['enemies']:
        pos.append(enemy['pos'])
    for enemy in l_state['enemies']:
        pos2.append(enemy['pos'])
    
    for x in range(len(pos)):
        if pos[x] == pos2[x]:
            return False
    return True

def is_already_free(game_state,mapa):
    for enemy in game_state['enemies']:
        if enemy['pos'][1] == 0 or enemy['pos'][1] == 1:
            return True
    return False