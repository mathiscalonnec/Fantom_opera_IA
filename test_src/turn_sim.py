from copy import deepcopy
from test_src.Node import Node
from test_src import game_utils as game
from test_src.globals import before, after, mandatory_powers, PlayerType
import test_src.character_sim as charsim

# BIG TODO: only keep node and depth in what you pass to functions (apart from character and special tings)
# TODO: maybe only calculate carlotta at the end

# NOTE: Here you can also just add character to game_state
# TODO: handle move with purple character power
def move(node: Node, depth: int, character, moved_character=None) -> list:
    final_nodes: list(Node) = []
    game_state = node.game_state
    characters_in_room = [
            q for q in game_state["characters"] if q["position"] == character["position"]]
    number_of_characters_in_room = len(characters_in_room)
    available_rooms = list()
    available_rooms.append(game.get_adjacent_positions_from_position(character["position"], character, game_state))
    for step in range(1, number_of_characters_in_room):
        # build rooms that are a distance equal to step+1
        next_rooms = list()
        for room in available_rooms[step-1]:
            next_rooms += game.get_adjacent_positions_from_position(room,
                                                                    character,
                                                                    game_state)
        available_rooms.append(next_rooms)
    # flatten the obtained list
    temp = list()
    for sublist in available_rooms:
        for room in sublist:
            temp.append(room)
    # filter the list in order to keep an unique occurrence of each room
    temp = set(temp)
    available_positions = list(temp)
    # ensure the character changes room
    if character["position"] in available_positions:
        available_positions.remove(character["position"])
    
    for player_choice in range(len(available_positions)):
        new_state = deepcopy(game_state)
        c_copy = deepcopy(character)
        selected_position = available_positions[player_choice]
        if c_copy["color"] == "brown" and c_copy["power"]:
            c_copy["position"] = selected_position
            
            if moved_character:
                moved_character["position"] = selected_position
                new_state = game.update_game_state_with_characters([moved_character], new_state)
        else:
            c_copy["position"] = selected_position            
        
        new_state = game.update_game_state_with_characters([c_copy], new_state)
        new_node = node.create_child(new_state, player_choice, depth, node.type, True)
        final_nodes.append(new_node)
    
    return final_nodes


# TODO: check beforehand if character needs to be played before
def activate_power_before(node: Node, depth: int, character):
    final_nodes: list(Node) = []
    game_state = node.game_state

    # If power not activated
    power_inactive_node = node.create_child(game_state, 0, depth + 1, node.type)
    final_nodes += move(power_inactive_node, depth, character)
    
    # If power activated
    c_copy = deepcopy(character)
    c_copy["power"] = True
    
    new_state = game.update_game_state_with_characters([c_copy], deepcopy(game_state))
    power_active_node = node.create_child(new_state, 1, depth + 1, node.type)
    if c_copy["color"] == "brown":
        final_nodes += charsim.brown_sim(power_active_node, depth + 1, c_copy, move)
    elif c_copy["color"] == "purple":
        final_nodes += charsim.purple_sim(power_active_node, depth + 1, c_copy)
    
    return final_nodes



def select(node: Node, depth: int, player_type: PlayerType) -> list:
    final_nodes: list(Node) = []
    game_state = node.game_state
    available_characters = game.get_active_characters_from_game_state(game_state)
    print('possible actions: ', available_characters)
    for player_choice in range(len(available_characters)):
        character = deepcopy(available_characters[player_choice])
        new_state = deepcopy(game_state)
        del new_state["active character_cards"][player_choice]
        new_node = node.create_child(new_state, player_choice, depth, player_type)
        print("select action: ", new_node.action)
        if character["color"] in before:
            final_nodes += activate_power_before(new_node, depth, character)
        else:
            final_nodes += move(new_node, depth + 1, character)

    return final_nodes


def simulate(node: Node, depth: int, player_type: PlayerType) -> list:
    final_nodes = select(node, depth + 1, player_type)
    return final_nodes