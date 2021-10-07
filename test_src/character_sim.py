from typing import Callable, Dict
from test_src.Node import Node
from test_src import game_utils as game
from copy import deepcopy

# defining type for callback move function
MoveFunc = Callable[[Node, int, Dict, Dict], list]


def brown_sim(node: Node, depth: int, character, callback: MoveFunc):
    final_nodes: list(Node) = []
    game_state = node.game_state
    # the brown character can take one other character with him
                    # when moving.
    characters = game.get_characters_from_game_state(game_state)
    available_characters = [q for q in characters if
                            character["position"] == q["position"] if
                            q["color"] != "brown"]

    # the socket can not take an object
    if len(available_characters) > 0:
        for i in  range(len(available_characters)):
            moved_character = available_characters[i]
            node.create_child(game_state, i, depth + 1, node.type)
            final_nodes += callback(node, depth + 1, character, deepcopy(moved_character))
    else:
        final_nodes += callback(node, depth, character)
    
    return final_nodes



def purple_sim(node: Node, depth: int, character):
    final_nodes: list(Node) = []
    game_state = node.game_state
    characters = game.get_characters_from_game_state(game_state)
    available_characters = [q for q in characters if
                            q["color"] != "purple"]

    for i in range(len(available_characters)):
        c_copy = deepcopy(character)
        selected_character = deepcopy(available_characters[i])
        # swap positions
        c_copy["position"], selected_character["position"] = selected_character["position"], c_copy["position"]
        # update game state
        new_state = game.update_game_state_with_characters([c_copy, selected_character], deepcopy(game_state))
        final_nodes.append(node.create_child(new_state, i, depth + 1, node.type, True))

    return final_nodes