#!/user/bin/env python3

from subprocess import Popen, PIPE, DEVNULL
from threading import Thread
from time import sleep
import os
from datetime import datetime
from typing import TextIO, Dict
from enum import Enum
import matplotlib.pyplot as plt


"""
    Script that runs a number of games until a convergence of winrate happens
    and then logs the results and recorded games in the directory defined by logs_dir
"""

# Here specify the files you want the script to launch
server_file = "./server.py"
inspector_file = "./calonnec_inspector.py"
fantom_file = "./calonnec_fantom.py"

# Directory where the results will be written
logs_dir = "test_results"

# Change this to True if you wish the games to be logged in output dir
game_logging_enabled = False

# Criteria used to evaluate distance between winrates at n and n -1
# (the lower it is, the better the winrate estimation gets and more the amount of
# games played is)
deviation_criteria = .1

min_nb_of_games = 10
inspector_wins = list()
fantom_wins = list()
fantom_winrate = []
x_data = []

class CharacterOccurences(object):

    def __init__(self):
        self.pink = 0
        self.blue = 0
        self.purple = 0
        self.grey = 0
        self.white = 0
        self.black = 0
        self.red = 0
        self.brown = 0
    
    def to_dict(self):
        return dict(vars(self))

success_rate_per_character = CharacterOccurences().to_dict()
success_rate_per_character_inspector = CharacterOccurences().to_dict()
success_rate_per_character_fantom = CharacterOccurences().to_dict()


def register_characters_played_for_win(characters_played: Dict, dest: Dict):
    for key, val in characters_played.items():
        dest[key] += val


def start_server(log_file: TextIO, game_number: int):
    server = Popen(['python3', server_file], stdout=PIPE, stderr=PIPE)
    stdout, stderr = server.communicate()
    inspector_turn = False
    occ_inspector = CharacterOccurences().to_dict()
    occ_fantom = CharacterOccurences().to_dict()

    output = stderr.decode().split('\n')
    for i, line in enumerate(output):
        if game_logging_enabled:
            log_file.write(line + '\n')

        if "inspector plays" in line:
            inspector_turn = True
        elif "fantom plays" in line:
            inspector_turn = False
        elif "inspector wins" in line:
            inspector_wins.append(game_number)
            fantom_winrate.append(len(fantom_wins) / len(x_data) * 100)
            register_characters_played_for_win(occ_inspector, success_rate_per_character)
            register_characters_played_for_win(occ_inspector, success_rate_per_character_inspector)
        elif "fantom wins" in line:
            fantom_wins.append(game_number)
            fantom_winrate.append(len(fantom_wins) / len(x_data) * 100)
            register_characters_played_for_win(occ_fantom, success_rate_per_character)
            register_characters_played_for_win(occ_fantom, success_rate_per_character_fantom)
        elif "select character" in line:
            keys = success_rate_per_character.keys()
            for color in keys:
                if color in output[i + 1]:
                    if inspector_turn:
                        occ_inspector[color] += 1
                    else:
                        occ_fantom[color] += 1
                    break


def start_player(file_name):
    proc = Popen(['python3', file_name], stdout=DEVNULL)
    proc.communicate()
    

def list_to_string(list: list):
    return ' '.join(str(e) for e in list)


def write_success_rates_per_character(res_file: TextIO, player_title: str, success_rates_per_cha: Dict):
        res_file.write('\n')
        sorted_tuples = sorted(success_rates_per_cha.items(), key=lambda x:x[1], reverse=True)
        sorted_characters = {k: v for k, v in sorted_tuples}
        for key, val in sorted_characters.items():
            res_file.write(f"{player_title} used {key} {val} times to win games\n")


def winrate_not_converged() -> bool:
    if len(fantom_winrate) < 2 or len(x_data) < min_nb_of_games:
        return True
    return abs(fantom_winrate[-1] - fantom_winrate[-2]) > deviation_criteria


if __name__ == '__main__':
    dir_name: str = datetime.now().strftime("%b-%d-%Y-%H:%M:%S")
    path_to_log_dir = os.path.join(logs_dir, dir_name)
    os.makedirs(path_to_log_dir)
    if game_logging_enabled:
        path_to_games_dir = os.path.join(path_to_log_dir, 'games')
        os.makedirs(path_to_games_dir)

    # Playing games until winrate convergence happens
    i = 1
    while winrate_not_converged():
        x_data.append(i)
        game_id = "game_" + str(i)
        print("playing game_" + str(i))

        log_file = None
        if game_logging_enabled:
            log_file = open(os.path.join(path_to_games_dir, (game_id + ".txt")), "w")

        server = Thread(target=start_server, args=(log_file, i + 1))
        inspector = Thread(target=start_player, args=(inspector_file,))
        fantom = Thread(target=start_player, args=(fantom_file, ))

        server.start()
        sleep(.5)
        inspector.start()
        sleep(.3)
        fantom.start()

        server.join()
        inspector.join()
        fantom.join()
        if game_logging_enabled:
            log_file.close()
        i += 1

    with open(os.path.join(path_to_log_dir, 'results.txt'), "w") as res_file:
        res_file.write(f"inspector win rate: {100 - fantom_winrate[-1]}" + '%\n')
        res_file.write(f"fantom win rate: {fantom_winrate[-1]}" + '%\n\n')
        res_file.write("games lost by inspector: " + list_to_string(fantom_wins) + '\n')
        res_file.write("game lost by fantom: " + list_to_string(inspector_wins) + '\n')
        write_success_rates_per_character(res_file, "players", success_rate_per_character)
        write_success_rates_per_character(res_file, "inspector", success_rate_per_character_inspector)
        write_success_rates_per_character(res_file, "fantom", success_rate_per_character_fantom)

    plt.plot(x_data, fantom_winrate, "o")
    plt.xlabel('games')
    plt.ylabel('% winrate (fantom)')
    plt.title(f"fantom win rate: {fantom_winrate[-1]}")
    plt.savefig(f"{path_to_log_dir}/fantom_winrate.pdf")
    plt.close()

    print(f"\nFinished testing, results written in {path_to_log_dir}")