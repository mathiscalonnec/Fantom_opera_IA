

# NOTE: obligé de reprendre exactement les mmes persos en jounat après chaque expansion
# NOTE: match state obtained with adversary plays against nodes of the tree to find where to play next

from random import random
from bernes_src.Node import Node
from bernes_src.GameReplica import Game
from bernes_src.PlayerReplica import Player
from copy import deepcopy

class Agent:
    """
        Agent working with tree strategy (max on every node for fantom)
        Last nodes: needs to be the one with the max stress
        Minimax on stress levels
    """
    current_node: Node
    end_nodes: list
    game: Game
    player: Player
    depth: int

    def __init__(self):
        self.player = Player(1)

    def __reset(self, game_state):
        self.depth = 0
        self.current_node = Node(0, 6, game_state)
        self.game = Game(self.player, game_state)


    def __backpropagate(self): # 
        best_val = 0
        index = 0
        for i in range(len(self.end_nodes)):
            if best_val < self.end_nodes[i].value:
                best_val = self.end_nodes[i].value
                index = i
        print('-------------- BEST VALUE', best_val)
        parent = self.end_nodes[index].parent
        while parent.parent is not None:
            parent.value = best_val
            parent = parent.parent


    def __expand(self, game, node):
        self.depth += 1
        possible_actions = game.get_next_possible_actions()
        for i in range(len(possible_actions)):
            new_game = deepcopy(game)
            new_game_state = game.answer(i)
            node.children.append(Node(self.depth, new_game_state.position_carlotta, new_game_state))
            if self.player.turn_end() is not True:
                self.__expand(new_game, node.children[-1])


    def __get_next_solution(self):
        val = 0
        index = 0
        for i in range(len(self.current_node.children)):
            if val < self.current_node.children[i].value:
                val = self.current_node.children[i].value
                index = i
        self.depth += 1
        self.current_node = self.current_node.children[index]
        return self.current_node.action


    def play(self, question: object) -> int:
        """
            Initializing the game again with the new state every time it's our turn
        """
        if question['question type'] == 'select character':
            print("select character")
            self.__reset(question["game state"])
            self.__expand(self.game, self.current_node)
            self.__backpropagate()

        elif "power" in question['question type']:
            print("power")
            return random.randint(0, len(question["data"]) - 1)

        return self.__get_next_solution()

