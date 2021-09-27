import json
import logging
import os
import random
import socket
from logging.handlers import RotatingFileHandler

import protocol

host = "localhost"
port = 12000
# HEADERSIZE = 10

"""
set up fantom logging
"""
fantom_logger = logging.getLogger()
fantom_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s :: %(levelname)s :: %(message)s", "%H:%M:%S")
# file
if os.path.exists("./logs/fantom.log"):
    os.remove("./logs/fantom.log")
file_handler = RotatingFileHandler('./logs/fantom.log', 'a', 1000000, 1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
fantom_logger.addHandler(file_handler)
# stream
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING)
fantom_logger.addHandler(stream_handler)


class Player():

    def __init__(self):

        self.end = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def connect(self):
        self.socket.connect((host, port))

    def reset(self):
        self.socket.close()

    def answer(self, question):
        # work
        data = question["data"]
        game_state = question["game state"]
        print_game_info(data, game_state)
        response_index = random.randint(0, len(data)-1)
        # log
        fantom_logger.debug("|\n|")
        fantom_logger.debug("fantom answers")
        fantom_logger.debug(f"question type ----- {question['question type']}")
        fantom_logger.debug(f"data -------------- {data}")
        fantom_logger.debug(f"response index ---- {response_index}")
        fantom_logger.debug(f"response ---------- {data[response_index]}")
        return response_index

    def handle_json(self, data):
        data = json.loads(data)
        response = self.answer(data)
        # send back to server
        bytes_data = json.dumps(response).encode("utf-8")
        protocol.send_json(self.socket, bytes_data)

    def run(self):

        self.connect()

        while self.end is not True:
            received_message = protocol.receive_json(self.socket)
            if received_message:
                self.handle_json(received_message)
            else:
                print("no message, finished learning")
                self.end = True


def print_game_info(data, game_state):
    print("DATA -----\n")
    print(data)
    print("-----\n")
    print("GAME State -----\n")
    print(game_state)
    print("-----\n")
    print(calculate_score(game_state))


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


def calculate_score(game_state):
    score = get_current_score_from_game_state(game_state)
    fantom = get_character_by_color(game_state, get_fantom_from_game_state(game_state))
    suspects = get_suspects_from_game_state(game_state)
    fantom_is_alone = is_character_alone(game_state, fantom["color"])

    if fantom["position"] == get_shadow_from_game_state(game_state) or fantom_is_alone:
        # Fantom alone or in the shadow / The Fantom shouts (score +1)
        score += 1
        for suspect in suspects:
            if is_character_alone(game_state, suspect["color"]):
                # Suspect alone (score +1)
                score += 1
                continue
            if suspect["position"] == get_shadow_from_game_state(game_state):
                # Suspect in the shadow (score +1)
                score += 1
    else:
        # Fantom in a group
        for suspect in suspects:
            if not is_character_alone(game_state, suspect["color"]) and not suspect["position"] == get_shadow_from_game_state(game_state):
                # Suspect not alone and not in the shadow / in a group (score +1)
                score += 1

    return score


p = Player()

p.run()
