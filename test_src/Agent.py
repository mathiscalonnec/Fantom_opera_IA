from typing import Dict
import random
from copy import deepcopy
import test_src.turn_sim as turn_sim
from test_src.Node import Node
from test_src import game_utils as game
from test_src.globals import PlayerType as pt
from test_src.TreeDisplay import TreeDisplay
import sys
import json


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

    # debug
    viz: TreeDisplay

    def __init__(self):
        self.current_node = None
        self.end_nodes = []
        
        self.turns = [pt.MIN, pt.MAX, pt.MAX, pt.MIN, pt.MAX, pt.MIN, pt.MIN, pt.MAX]
        self.fantom_turns = [1, 2, 4, 7]

        # debug
        self.viz = TreeDisplay()


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
        res_nodes: list(Node) = turn_sim.simulate(node, current_depth, self.turns[turn])
        
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
        for i in range(len(self.current_node.children)):
            if player_type is pt.MAX and val < self.current_node.children[i].value:
                val = self.current_node.children[i].value
                index = i
            elif player_type is pt.MIN and val > self.current_node.children[i].value:
                val = self.current_node.children[i].value
                index = i
        self.current_node = self.current_node.children[index]
        return self.current_node.action



    def play(self, question: object, debug=True) -> int:
        question_type = question["question type"]
        turn = self.fantom_turns[(question["game state"]["num_tour"] - 1) % len(self.fantom_turns)] 
        if question_type == 'select character':
            # create or recreate tree, reinitialising sim to current turn
            self.__init_tree(question["game state"], turn)
            self.__expand(self.current_node, 0, turn)
            self.__backpropagate()

        elif "brown" or "purple" not in question_type and "power" in question_type:
            return random.randint(0, len(question["data"]) - 1)
        if debug and turn == 1:
            self.viz.create_frame(self.current_node)

        return self.__get_next_solution(self.turns[turn])

