from typing import Dict
from test_src import game_utils as game

"""
    All actions get at least:
        - game_state
        - index of the data chosen
    and return at least:
        - new game_state

    Power is never activated for each character
"""

class Actions:
    character: Dict
    moved_character: Dict
    available_positions: list


    def __init__(self):
        self.character = None
        self.moved_character = None
        self.available_positions = None


    def get_possible_actions_for_select(self, game_state):
        # Here, start of a new turn so we reset chosen character and moved characters
        if self.character:
            self.__init__()
        return game_state["active character_cards"]


    def execute_select(self, game_state, player_choice: int):
        available_characters = game.get_active_characters_from_game_state(game_state)
        if player_choice not in range(len(available_characters)):
            raise Exception("execute_select: incorrect choice index")
        chosen_character = available_characters[player_choice]
        # del available_characters[player_choice]
        self.character = chosen_character


    # TODO: handle move with purple character power
    def get_possible_actions_for_move(self, game_state):
        characters_in_room = [
                q for q in game_state["characters"] if q["position"] == self.character["position"]]
        number_of_characters_in_room = len(characters_in_room)
        available_rooms = list()
        available_rooms.append(game.get_adjacent_positions_from_position(self.character["position"], self.character, game_state))
        for step in range(1, number_of_characters_in_room):
            # build rooms that are a distance equal to step+1
            next_rooms = list()
            for room in available_rooms[step-1]:
                next_rooms += game.get_adjacent_positions_from_position(room,
                                                                        self.character,
                                                                        game_state)
            available_rooms.append(next_rooms)
        # flatten the obtained list
        temp = list()
        for sublist in available_rooms:
            for room in sublist:
                temp.append(room)

        # filter the list in order to keep an unique occurrence of each room
        temp = set(temp)
        self.available_positions = list(temp)

        # ensure the character changes room
        if self.character["position"] in self.available_positions:
            self.available_positions.remove(self.character["position"])
        return self.available_positions


    def execute_move(self, game_state, player_choice):
        if player_choice not in range(len(self.available_positions)):
            raise Exception("execute_move: , incorrect choice index")
        selected_position = self.available_positions[player_choice]
        if self.character["color"] == "brown" and self.character["power"]:
            self.character["position"] = selected_position
            if self.moved_character:
                self.moved_character["position"] = selected_position
        else:
            self.character["position"] = selected_position

