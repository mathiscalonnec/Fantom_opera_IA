from typing import Dict, Set, List
from test_src.Character import Character
from copy import deepcopy

"""
    All actions get at least:
        - game_state
        - value of the action to be done
        - index of the data chosen
    and return at least:
        - new game_state
"""


class Actions:


    def select(self, game_state, player_choice: int) -> Set(Character, Dict):
        state = deepcopy(game_state)
        available_characters = state["active character_cards"]
        if player_choice not in range(len(available_characters)):
            raise Exception("SELECT: incorrect choice index")
        chosen_char = available_characters[player_choice]
        del available_characters[chosen_char]
        return {
            "chosen_character": chosen_char,
            "game_state": state
        }


    def move(self, game_state):
        state = deepcopy(game_state)
        print("move")

    