#!/user/bin/env python3

from subprocess import Popen, PIPE, DEVNULL
from sys import stderr
from threading import Thread
from time import sleep
import os
from datetime import datetime
from typing import TextIO
import matplotlib.pyplot as plt
import numpy as np
from numpy.lib.function_base import average


server_file = "./server.py"
inspector_file = "./random_inspector.py"
fantom_file = "./test_fantom.py"

logs_dir = "test_results"

min_nb_of_games = 10
inspector_wins = list()
fantom_wins = list()
fantom_winrate = []
deviation_criteria = .1
x_data = []


def start_server(log_file: TextIO, game_number: int):
    server = Popen(['python3', server_file], stdout=PIPE, stderr=PIPE)
    stdout, stderr = server.communicate()
    no_error = False
    for line in stderr.decode().split('\n'):
        log_file.write(line + '\n')
        if "inspector wins" in line:
            inspector_wins.append(game_number)
            fantom_winrate.append(len(fantom_wins) / len(x_data) * 100)
            no_error = True
        elif "fantom wins" in line:
            fantom_wins.append(game_number)
            fantom_winrate.append(len(fantom_wins) / len(x_data) * 100)
            no_error = True
    if no_error is False:
        x_data.pop()        


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

        log_file = open(os.path.join(path_to_log_dir, (game_id + ".json")), "w")

        server = Thread(target=start_server, args=(log_file, i + 1))
        inspector = Thread(target=start_player, args=(inspector_file,))
        fantom = Thread(target=start_player, args=(fantom_file, ))

        server.start()
        sleep(.5)
        inspector.start()
        fantom.start()

        server.join()
        inspector.join()
        fantom.join()
        log_file.close()
        i += 1

    with open(os.path.join(path_to_log_dir, 'results.txt'), "w") as res_file:
        res_file.write("inspector win rate: " + str(int(len(inspector_wins) / len(x_data) * 100)) + '%\n')
        res_file.write("fantom win rate: " + str(int(len(fantom_wins) / len(x_data) * 100)) + '%\n\n')
        res_file.write("games lost by inspector: " + list_to_string(fantom_wins) + '\n')
        res_file.write("game lost by fantom: " + list_to_string(inspector_wins) + '\n')

    x =  np.array(x_data)
    y = np.array(fantom_winrate)
    plt.plot(x, y, "o")
    plt.xlabel('games')
    plt.ylabel('% winrate (fantom)')
    plt.title(f"fantom win rate: {fantom_winrate[-1]}")
    plt.savefig(f"{path_to_log_dir}/winrate.pdf")
    plt.close()