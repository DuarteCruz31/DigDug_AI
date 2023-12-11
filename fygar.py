class fygar_moves:
    def __init__(self, id, move):
        self.id = id
        self.move = move
        self.next = None
    
    def __str__(self):
        return "x: {} /// y: {}".format(self.move[0], self.move[1])

class Last4MovesList:
    def __init__(self):
        self.head = None

    def add_move(self, move):
        if self.head is None:
            new_node = fygar_moves(1, move)
            self.head = new_node
        else:
            new_node = fygar_moves(self.head.id + 1, move)
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node

            if self.count_moves() > 3:
                self.head = self.head.next

    def display_moves(self):
        current = self.head
        while current:
            print(current)
            current = current.next

    def count_moves(self):
        count = 0
        current = self.head
        while current:
            count += 1
            current = current.next
        return count

    def has_repeated_values(self):
        seen_values = set()
        current = self.head

        while current is not None:
            if current.move in seen_values:
                return True

            seen_values.add(current.move)
            current = current.next

        return False


