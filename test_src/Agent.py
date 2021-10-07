from typing import Dict
import random
from copy import deepcopy
import test_src.turn_sim as turn_sim
from test_src.Node import Node
from test_src import game_utils as game
from test_src.globals import PlayerType as pt
import sys
import json

# BIG TODO: maybe do a visual representation of tree after being generated -> better debug
# Beforehand you would need to indicate at which node action that is being executed

class Agent:
    """
        TODO:
         - Character powers (for now, always deactivated)
         - Take into account inspector turns -> tree longer than for one turn
         - maybe define a max depth ?? (if necessary)
    """
    current_node: Node
    end_nodes: list

    turns: list
    fantom_turns = list

    def __init__(self):
        self.current_node = None
        self.end_nodes = []
        
        self.turns = [pt.MIN, pt.MAX, pt.MAX, pt.MIN, pt.MAX, pt.MIN, pt.MIN, pt.MAX]
        self.fantom_turns = [1, 2, 4, 7]

        self.max_depth = 4


    def __init_tree(self, game_state, turn: int):
        self.current_node = Node(0, 0, 6, game_state, self.turns[turn])


    def clone(self, obj: Dict):
        return json.loads(json.dumps(obj))


    def __backpropagate(self): 
        end_nodes = deepcopy(self.end_nodes)
        while len(end_nodes) > 0:
            current_type = end_nodes[0].parent.type
            # sorting end nodes to have MIN value first if MAX and MAX value first if MIN
            # that way we populate higher nodes with least important value first
            end_nodes = sorted(end_nodes, 
                                key= lambda e: e.value,
                                reverse= current_type == pt.MIN
                                )
            new_end_nodes = list()
            # backpropagating the values,
            # making sure that higher values override lower ones if MAX and 
            # lower values override higher ones if MIN
            for node in end_nodes:
                val = node.value
                node = node.parent
                while node.parent is not None and node.parent.type is current_type:
                    node.value = val
                    node = node.parent
                # Adding value to top nodes of the same type
                node.value = val 
                if node.parent is not None:
                    new_end_nodes.append(node)
            end_nodes = new_end_nodes


    # TODO: find a way to handle end condition nicely (in case one player wins)
    def __expand(self, node: Node, current_depth: int, turn: int):
        res_nodes: list(Node) = turn_sim.simulate(node, current_depth)
        
        if len(res_nodes) == 0 or turn + 1 >= len(self.turns):
            self.end_nodes += res_nodes
        else: 
            for e in res_nodes:
                self.__expand(e, e.depth, turn + 1)

        

    # TODO: start at type of interest (& where characters match)
    # TODO: maybe check if turn and question type are correct
    def __get_next_solution(self, player_type: pt):
        val = 0
        index = 0
        print("depth: ", self.current_node.depth)
        print("type: ", self.current_node.type)
        for i in range(len(self.current_node.children)):
            print("test: ", self.current_node.children[i].value)
            if player_type is pt.MAX and val < self.current_node.children[i].value:
                val = self.current_node.children[i].value
                index = i
            elif player_type is pt.MIN and val > self.current_node.children[i].value:
                val = self.current_node.children[i].value
                index = i
        print("VAL : ", val)
        self.current_node = self.current_node.children[index]
        return self.current_node.action



    # TODO: check -> you get turn 2 times in a row
    def play(self, question: object) -> int:
        """
            Initializing the tree again with the new state every time it's our turn
        """
        turn = self.fantom_turns[(question["game state"]["num_tour"] - 1) % len(self.fantom_turns)] 
        print('---------------------')
        print("question type: ", question['question type'])
        print('num_tour: ', question["game state"]["num_tour"])
        print('- turn: ', turn)
        if question['question type'] == 'select character':
            # create or recreate tree, reinitialising sim to current turn
            self.__init_tree(question["game state"], turn)
            self.__expand(self.current_node, 0, turn)
            self.__backpropagate()

        elif "power" in question['question type']:
            return random.randint(0, len(question["data"]) - 1)

        return self.__get_next_solution(self.turns[turn])

