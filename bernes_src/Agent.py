

# NOTE: obligé de reprendre exactement les mmes persos en jounat après chaque expansion
# NOTE: match state obtained with adversary plays against nodes of the tree to find where to play next

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
    end_nodes: list(Node)
    game: Game
    player: Player
    depth: int

    def __init__(self):
        self.player = Player(1)

    def __find_best_value(self):
        # finding best value & node index associated
        best_val = 0
        index = 0
        for i in range(len(self.end_nodes)):
            if best_val < self.end_nodes[i].value:
                best_val = self.end_nodes[i].value
                index = i
        # TODO: check if something breaks here
        parent = self.end_nodes[index].parent
        while parent.parent is not None:
            parent.value = best_val
            parent = parent.parent


    def __expand(self, game, node):
        self.depth += 1
        possible_actions = game.get_next_possible_actions() # TODO: do this func
        for action in possible_actions:
            new_game = deepcopy(game)
            new_game_state = new_game.get_action_res(action)
            # TODO: end condition and create end_nodes
            node.children.append(Node(self.depth, new_game_state.position_carlotta, new_game_state))
            self.__expand(new_game, node.children[-1])


    def __get_next_solution(self):
        self.depth += 1
        val = 0
        index = 0
        for i in range(len(self.current_node.children)):
            if val < self.current_node.children[i].value:
                val = self.current_node.children[i].value
                index = i
        self.current_node = self.current_node.children[index]
        return self.current_node.action


    def __find_next_solution(self, question: object) -> int:
        """
            Initializing the game again with the new state every time it's our turn
        """
        if question['question type'] == 'select character':
            # Reset the whole tree
            self.depth = 0
            print("----received game state: ", question['game state'])
            self.current_node = Node(0, 6, question['game state'])
            self.game = Game(self.player, question["game state"])
            self.__expand(self.game, self.node)
            print("++++REGISTERED GAME STATE: ", self.game.game_state)
            # self.__expand
        return self.__get_next_solution()


    def play(self, question: object) -> int:
        # if self.turn_index % self.max_search_depth == 0:
        #     self.__expand()

        return self.__find_next_solution(question)
