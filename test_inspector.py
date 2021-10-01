import json
import logging
import os
import random
import socket
from logging.handlers import RotatingFileHandler
from typing import List

import protocol

host = "localhost"
port = 12000
# HEADERSIZE = 10
passages = [{1, 4}, {0, 2}, {1, 3}, {2, 7}, {0, 5, 8},
            {4, 6}, {5, 7}, {3, 6, 9}, {4, 9}, {7, 8}]

character_using_direction = 0

"""
set up inspector logging
"""
inspector_logger = logging.getLogger()
inspector_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s :: %(levelname)s :: %(message)s", "%H:%M:%S")
# file
if os.path.exists("./logs/inspector.log"):
    os.remove("./logs/inspector.log")
file_handler = RotatingFileHandler('./logs/inspector.log', 'a', 1000000, 1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
inspector_logger.addHandler(file_handler)
# stream
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING)
inspector_logger.addHandler(stream_handler)

def print_game_info(data, game_state):
    print("DATA -----\n")
    print(data)
    print("-----\n")
    print("GAME State -----\n")
    print(game_state)
    print("-----\n")
    print("Update Game_State Suspects -----\n")
    print(get_suspects_from_game_state(update_game_state_suspects(game_state)))
    print("-----\n")

def get_current_score_from_game_state(game_state):
    return game_state["position_carlotta"]


def get_shadow_from_game_state(game_state):
    return game_state["shadow"]


def get_blocked_from_game_state(game_state):
    return game_state["blocked"]


def get_fantom_from_game_state(game_state):
    return game_state["fantom"]


def get_characters_from_game_state(game_state):
    return game_state["characters"]


def get_suspects_from_game_state(game_state):
    suspects = []

    for character in game_state["characters"]:
        if character["suspect"]:
            suspects.append(character)
    return suspects


def get_active_characters_from_game_state(game_state):
    return game_state["active character_cards"]


def get_character_by_color(game_state, color):
    target = {}
    for character in get_characters_from_game_state(game_state):
        if character["color"] == color:
            target = character
            break
    return target


def get_characters_by_position(game_state, position):
    targets = []
    for character in get_characters_from_game_state(game_state):
        if character["position"] == position:
            targets.append(character)
    return targets


def is_character_alone(game_state, color):
    character = get_character_by_color(game_state, color)
    nb = len(get_characters_by_position(game_state, character["position"]))

    return True if nb == 1 else False

def get_number_of_suspects_from_game_state(game_state):
    return(len(get_suspects_from_game_state(game_state)))


def get_suspects_alone_or_shadow(game_state):
    character = get_suspects_from_game_state(game_state)
    char_alone = []
    shadow = get_shadow_from_game_state(game_state)

    for element in character:
        if is_character_alone(game_state, element["color"]):
            char_alone.append(element)
        elif (element["position"] == shadow):
            char_alone.append(element)

    return(char_alone)

def is_character_in_shadow(game_state, color):
    character = get_character_by_color(game_state, color)

    return character["position"] == get_shadow_from_game_state(game_state)



def update_game_state_suspects(game_state):
    fantom = get_character_by_color(game_state, get_fantom_from_game_state(game_state))
    suspects = get_suspects_from_game_state(game_state)
    fantom_is_alone = is_character_alone(game_state, fantom["color"])

    if fantom["position"] == get_shadow_from_game_state(game_state) or fantom_is_alone:
        for suspect in suspects:
            if not is_character_alone(game_state, suspect["color"]) \
                    and not is_character_in_shadow(game_state, suspect["color"]):
                for character in get_characters_from_game_state(game_state):
                    if suspect["color"] == character["color"]:
                        character["suspect"] = False
                        break
    else:
        for suspect in suspects:
            if is_character_alone(game_state, suspect["color"]):
                for character in get_characters_from_game_state(game_state):
                    if suspect["color"] == character["color"]:
                        character["suspect"] = False
                        break
                continue
            if is_character_in_shadow(game_state, suspect["color"]):
                for character in get_characters_from_game_state(game_state):
                    if suspect["color"] == character["color"]:
                        character["suspect"] = False
                        break

    return game_state


def predict_turn(game_state, depth, predictions):
    # TODO fix depth
    predictions.append({"depth": depth, "data": {"color": "", "position": 0, "power": False, "power_action": 0}})
    if depth > 0:
        predict_turn(game_state.copy(), depth - 1, predictions)
        print("depth ", depth)


def play_turn(game_state, turn_answer):
    depth = 0
    depth = len(game_state["active character_cards"]) - 1
    predictions = []

    predict_turn(game_state, depth, predictions)

    print("predictions ", predictions)

    # TODO select best score
    # answer = best answer from list
    # turn_answer["color"] = ...
    # turn_answer["position"] = ...
    # turn_answer["power"] = ...
    # turn_answer["power_action"] = ...

    return turn_answer

class Game_inspector:
    game_state: list
    new_game_state: list
    score: int
    characters: list
    character_using_index: int    
    character_using_direction: int
    blocked: list

    def __init__(self, game_state, characters):
        self.game_state = game_state
        self.score = self.calculate_score(game_state)
        self.new_game_state = game_state
        self.characters = characters
        self.character_using_index = None
        self.character_using_direction = None
        self.blocked = game_state["blocked"]

    def calculate_score(self, game_state):
        number_of_suspects = get_number_of_suspects_from_game_state(game_state)
        number_of_suspects_alone = len(get_suspects_alone_or_shadow(game_state))
        number_of_suspects_in_group = number_of_suspects - number_of_suspects_alone
        score = abs(number_of_suspects_in_group - number_of_suspects_alone)
        #the goal for the inspector is to have a score near zero
        return (score)

    def find_best_score(self, index_char, character):
        position_in_game_state = self.game_state["characters"].index(character)
        position = character["position"]
        game_state_tmp = self.game_state

        for element in passages[position]:
            game_state_tmp["characters"][position_in_game_state]["position"] = element
            new_score = self.calculate_score(game_state_tmp)
            if ((element in self.blocked) == False):
                if(self.character_using_direction == None):
                    self.score = new_score
                    self.character_using_index = index_char
                    self.character_using_direction = element
                if new_score == self.score:
                    self.score = new_score
                    self.character_using_index = index_char
                    self.character_using_direction = element
                    if self.score == 0:
                      break


    def chose_character(self):
        for element in self.characters:
            self.characters.index(element)
            self.find_best_score(self.characters.index(element), element)
            if self.score == 0:
                break

    def run(self):
        self.chose_character()


class Player():

    def __init__(self):

        self.end = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def connect(self):
        self.socket.connect((host, port))

    def reset(self):
        self.socket.close()

    def answer(self, question, turn_answer):
        # work
        data = question["data"]
        game_state = question["game state"]
        # print_game_info(data, game_state)
        response_index = 0
        inspector = Game_inspector(game_state, data)

        if question["question type"] == "select character":
            inspector.run()
            response_index = inspector.character_using_index
            global character_using_direction
            character_using_direction = inspector.character_using_direction

        elif question["question type"] == "select position":
            response_index = data.index(character_using_direction)

        else:
            # TODO Need to add specific question for power
            response_index = 1 if turn_answer["power"] else 0

        # log
        inspector_logger.debug("|\n|")
        inspector_logger.debug("inspector answers")
        inspector_logger.debug(f"question type ----- {question['question type']}")
        inspector_logger.debug(f"data -------------- {data}")
        inspector_logger.debug(f"response index ---- {response_index}")
        inspector_logger.debug(f"response ---------- {data[response_index]}")
        return response_index

    def handle_json(self, data, turn_answer):
        data = json.loads(data)
        response = self.answer(data, turn_answer)
        # send back to server
        bytes_data = json.dumps(response).encode("utf-8")
        protocol.send_json(self.socket, bytes_data)

    def run(self):

        self.connect()

        turn_answer = {"color": "", "position": 0, "power": False, "power_action": 0}

        while self.end is not True:
            received_message = protocol.receive_json(self.socket)
            if received_message:
                self.handle_json(received_message, turn_answer)
            else:
                print("no message, finished learning")
                self.end = True


p = Player()

p.run()
