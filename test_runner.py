#!/user/bin/env python3

from subprocess import Popen, PIPE, DEVNULL
from threading import Thread
from time import sleep
import os
from datetime import datetime
from typing import TextIO
import matplotlib.pyplot as plt


"""
    Script that runs a number of games until a convergence of winrate happens
    and then logs the results and recorded games in the directory defined by logs_dir
"""


server_file = "./server.py"
inspector_file = "./random_inspector.py"
fantom_file = "./test_fantom.py"

deviation_criteria = .2

logs_dir = "test_results"
min_nb_of_games = 10
inspector_wins = list()
fantom_wins = list()
fantom_winrate = []
x_data = []


def start_server(log_file: TextIO, game_number: int):
    server = Popen(['python3', server_file], stdout=PIPE, stderr=PIPE)
    stdout, stderr = server.communicate()
    for line in stderr.decode().split('\n'):
        log_file.write(line + '\n')
        if "inspector wins" in line:
            inspector_wins.append(game_number)
            fantom_winrate.append(len(fantom_wins) / len(x_data) * 100)
        elif "fantom wins" in line:
            fantom_wins.append(game_number)
            fantom_winrate.append(len(fantom_wins) / len(x_data) * 100)


def start_player(file_name):
    proc = Popen(['python3', file_name], stdout=DEVNULL)
    proc.communicate()
    

def list_to_string(list: list):
    return ' '.join(str(e) for e in list)


def winrate_not_converged() -> bool:
    if len(fantom_winrate) < 2 or len(x_data) < min_nb_of_games:
        return True
    return abs(fantom_winrate[-1] - fantom_winrate[-2]) > deviation_criteria


if __name__ == '__main__':
    dir_name: str = datetime.now().strftime("%b-%d-%Y-%H:%M:%S")
    path_to_log_dir = os.path.join(logs_dir, dir_name)
    os.makedirs(path_to_log_dir)

    i = 1
    while winrate_not_converged():
        x_data.append(i)
        game_id = "game_" + str(i)
        print("playing game_" + str(i))

        log_file = open(os.path.join(path_to_log_dir, (game_id + ".txt")), "w")

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
        log_file.close()
        i += 1

    with open(os.path.join(path_to_log_dir, 'results.txt'), "w") as res_file:
        res_file.write(f"inspector win rate: {100 - fantom_winrate[-1]}" + '%\n')
        res_file.write(f"fantom win rate: {fantom_winrate[-1]}" + '%\n\n')
        res_file.write("games lost by inspector: " + list_to_string(fantom_wins) + '\n')
        res_file.write("game lost by fantom: " + list_to_string(inspector_wins) + '\n')

    plt.plot(x_data, fantom_winrate, "o")
    plt.xlabel('games')
    plt.ylabel('% winrate (fantom)')
    plt.title(f"fantom win rate: {fantom_winrate[-1]}")
    plt.savefig(f"{path_to_log_dir}/winrate.pdf")
    plt.close()