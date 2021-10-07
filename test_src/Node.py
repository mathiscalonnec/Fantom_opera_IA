from test_src.globals import PlayerType
from test_src import game_utils as game

class Node:

    parent: object
    children: list[object]
    depth: int
    value: int
    character: str

    def __init__(self, action, depth, value, game_state, type: PlayerType, prev=None):
        self.parent = prev
        self.children = []

        self.depth = depth
        self.value: int = value
        self.action: int = action
        self.game_state: object = game_state
        self.type = type


    # TODO: check if typecast works here
    def create_child(self, game_state, action: int, depth: int, player_type: PlayerType, calculate_score=False) -> "Node":
        self.children.append(Node(
                action,
                depth,
                game.calculate_score(game_state) if calculate_score else self.value,
                game_state,
                player_type,
                self
        ))
        return self.children[-1]
