

# NOTE: obligé de reprendre exactement les mmes persos en jounat après chaque expansion
# NOTE: match state obtained with adversary plays against nodes of the tree to find where to play next

from random import random
from test_src import Actions
from test_src.Node import Node
from copy import deepcopy
from test_src.Actions import actions

class Agent:
    """
        TODO:
         - Character powers (for now, always deactivated)
         - Take into account inspector turns -> tree longer than for one turn
    """
    current_node: Node
    end_nodes: list
    depth: int

    actions: Actions

    def __init__(self, game_state):
        self.depth = 0
        self.current_node = Node(0, 6, game_state)
        self.actions = Actions()


    def __backpropagate(self): # 
        best_val = 0
        index = 0
        for i in range(len(self.end_nodes)):
            if best_val < self.end_nodes[i].value:
                best_val = self.end_nodes[i].value
                index = i
        parent = self.end_nodes[index].parent
        while parent.parent is not None:
            parent.value = best_val
            parent = parent.parent


    def __expand(self, game_state, node):
        self.depth += 1
        possible_actions = self.actions.get_select_possible_actions(game_state)
        for i in range(len(possible_actions)):
            new_state = self.actions.execute_select(game_state, possible_actions[i])
            node.children.append(Node(self.depth, new_state["position_carlotta"], new_state))
            print(node)
            # if self.player.turn_end() is not True:
            #     self.__expand(new_game, node.children[-1])


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

