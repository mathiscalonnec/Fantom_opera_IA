

# NOTE: obligé de reprendre exactement les mmes persos en jounat après chaque expansion
# NOTE: match state obtained with adversary plays against nodes of the tree to find where to play next

from typing import Dict
from random import random
from copy import deepcopy
from test_src.Actions import Actions
from test_src.Node import Node
from test_src import game_utils as game


class Agent:
    """
        TODO:
         - Character powers (for now, always deactivated)
         - Take into account inspector turns -> tree longer than for one turn
    """
    current_node: Node
    end_nodes: list

    actions: Actions

    questions: list
    actions_to_execute: list

    def __init__(self):
        self.current_node = None
        self.end_nodes = []
        self.actions = Actions()
        self.questions = [self.actions.get_possible_actions_for_select, self.actions.get_possible_actions_for_move]
        self.actions_to_execute = [self.actions.execute_select, self.actions.execute_move]


    def __init_tree(self, game_state):
        self.current_node = Node(0, 6, game_state)


    # TODO: here do not only propagate best value but also other values first (if opponent doesn't choose max or min)
    def __backpropagate(self): 
        best_val = 0
        index = 0
        for i in range(len(self.end_nodes)):
            if best_val < self.end_nodes[i].value:
                best_val = self.end_nodes[i].value
                index = i
        node = self.end_nodes[index] # .parent
        while node.parent is not None:
            node.value = best_val
            node = node.parent


    def __expand_end_condition(self, depth):
        return depth >= len(self.questions)


    def __expand(self, game_state: Dict, node: Node, depth: int):
        action_index = depth % len(self.questions)
        possible_actions = self.questions[action_index](game_state)
        depth += 1

        for i in range(len(possible_actions)):
            new_state = deepcopy(game_state)
            self.actions_to_execute[action_index](new_state, i)
            new_state = game.update_game_state_suspects(new_state)
            node.children.append(Node(depth - 1, game.calculate_score(new_state), new_state, node))
            if self.__expand_end_condition(depth) is False:
                self.__expand(new_state, node.children[-1], depth)

        if self.__expand_end_condition(depth):
            self.end_nodes.extend(node.children)


    def __get_next_solution(self):
        val = 0
        index = 0
        for i in range(len(self.current_node.children)):
            if val < self.current_node.children[i].value:
                val = self.current_node.children[i].value
                index = i
        self.current_node = self.current_node.children[index]
        return self.current_node.action



    def play(self, question: object) -> int:
        """
            Initializing the game again with the new state every time it's our turn
        """
        if question['question type'] == 'select character':
            # create or recreate tree
            self.__init_tree(question["game state"])
            self.__expand(question["game state"], self.current_node, 0)
            self.__backpropagate()

        elif "power" in question['question type']:
            return 0 # random.randint(0, len(question["data"]) - 1)

        return self.__get_next_solution()

