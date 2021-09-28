
class Node:

    parent: object
    children: list[object]
    depth: int
    value: int
    character: str

    def __init__(self, depth, value, game_state, prev=None):
        self.parent = prev
        self.children = []
        self.depth = depth
        self.value: int = value
        self.action: int = 0
        self.game_state: object = game_state