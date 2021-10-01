#!/user/bin/env python3

from subprocess import Popen, PIPE, DEVNULL
from sys import stderr
from threading import Thread
from time import sleep
import os
from datetime import datetime
from typing import TextIO


nb_of_games_to_be_played = 10

server_file = "./server.py"
inspector_file = "./random_inspector.py"
fantom_file = "./test_fantom.py"

logs_dir = "test_logs"

inspector_wins = list()
fantom_wins = list()

def start_server(log_file: TextIO, game_number: int):
    server = Popen(['python3', server_file], stdout=PIPE, stderr=PIPE)
    stdout, stderr = server.communicate()
    for line in stderr.decode().split('\n'):
        log_file.write(line + '\n')
        if "inspector wins" in line:
            inspector_wins.append(game_number)
        elif "fantom wins" in line:
            fantom_wins.append(game_number)


def start_player(file_name):
    proc = Popen(['python3', file_name], stdout=DEVNULL)
    proc.communicate()
    

def list_to_string(list: list):
    return ' '.join(str(e) for e in list)

if __name__ == '__main__':
    # create log dir
    dir_name: str = datetime.now().strftime("%b-%d-%Y-%H:%M:%S")
    path_to_log_dir = os.path.join(logs_dir, dir_name)
    os.makedirs(path_to_log_dir)

    for i in range(nb_of_games_to_be_played):
        game_id = "game_" + str(i + 1)
        print("playing ", game_id)

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

    with open(os.path.join(path_to_log_dir, 'results.txt'), "w") as res_file:
        res_file.write("inspector win rate: " + str(int(len(inspector_wins) / nb_of_games_to_be_played * 100)) + '%\n')
        res_file.write("fantom win rate: " + str(int(len(fantom_wins) / nb_of_games_to_be_played * 100)) + '%\n\n')
        res_file.write("games lost by inspector: " + list_to_string(fantom_wins) + '\n')
        res_file.write("game lost by fantom: " + list_to_string(inspector_wins) + '\n')