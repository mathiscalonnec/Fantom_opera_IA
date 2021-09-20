import json
from random import shuffle, randrange, choice
from typing import List, Set, Union, Tuple

from src.Character import Character
from bernes_src.PlayerReplica import Player
from bernes_src.globals_replica import passages, colors


class Game:
    """
        Class representing a full game until either the inspector
        of the fantom wins.
    """
    # players: List[Player]
    player: Player
    position_carlotta: int
    exit: int
    num_tour: int
    shadow: int
    blocked: Tuple[int]
    characters: Set[Character]
    character_cards: List[Character]
    active_cards: List[Character]
    cards: List[Union[Character, str]]
    fantom: Character

    # Todo: def __init__ should be __init__(self, player_1: Player, player_2:
    #  Player)
    def __init__(self, player: Player, game_state: object): # players: List[Player]):
        # Todo: Should be self.players: Tuple[Player] = (player_1, player_2)
        # self.players = players
        self.player = player
        self.position_carlotta = game_state['position_carlotta']
        # Todo: Should be removed and make the game ends when carlotta reach 0.
        self.exit = game_state['exit']
        self.num_tour = game_state['num_tour']
        # Todo: Should be a Dict[enum, Character]
        self.characters = game_state['characters']
        # character_cards are used to draw 4 characters at the beginning
        # of each round
        # TODO: replace next line -> game_state['character_cards'] represents the display
        self.character_cards = game_state['character_cards']
        self.active_cards = game_state["active character_cards"]
        self.alibi_cards = self.character_cards.copy()
        self.fantom = next(card for card in self.alibi_cards if card['color'] == game_state['fantom'])
        self.alibi_cards.remove(self.fantom)
        self.alibi_cards.extend(['fantom'] * 3)

        self.shadow = game_state['shadow']
        self.blocked = game_state['blocked']


        self.characters_display = [character for character in self.characters]
        self.character_cards_display = [tile for tile in self.character_cards]
        self.active_cards_display = [tile for tile in self.active_cards]
        
        # TODO: nex lines to be decommented
        # self.characters_display = [character.display() for character in
        #                            self.characters]
        # self.character_cards_display = [tile.display() for tile in
        #                                 self.character_cards]
        # self.active_cards_display = [tile.display() for tile in
        #                              self.active_cards]

        # TODO: reassign game state every time new move from inspector
        self.game_state = {
            "position_carlotta": self.position_carlotta,
            "exit": self.exit,
            "num_tour": self.num_tour,
            "shadow": self.shadow,
            "blocked": self.blocked,
            "characters": self.characters_display,
            # Todo: should be removed
            "character_cards": self.character_cards_display,
            "active character_cards": self.active_cards_display,
        }

    def actions(self):
        self.active_cards = "" # TODO: here reassign active cards (or before)
        for card in self.active_cards:
            card.power_activated = False
        self.player.play(self)

    def fantom_scream(self):
        partition: List[Set[Character]] = [
            {p for p in self.characters if p.position == i} for i in range(10)]
        if len(partition[self.fantom.position]) == 1 \
                or self.fantom.position == self.shadow:
            self.position_carlotta += 1
            for room, chars in enumerate(partition):
                if len(chars) > 1 and room != self.shadow:
                    for p in chars:
                        p.suspect = False
        else:
            for room, chars in enumerate(partition):
                if len(chars) == 1 or room == self.shadow:
                    for p in chars:
                        p.suspect = False
        self.position_carlotta += len(
            [p for p in self.characters if p.suspect])

    # TODO: get next possible actions -> return an array
    def tour(self):
        # work
        self.actions()
        # self.fantom_scream()
        return 

    def __repr__(self):
        message = f"Tour: {self.num_tour},\n" \
            f"Position Carlotta / exit: {self.position_carlotta}/{self.exit},\n" \
            f"Shadow: {self.shadow},\n" \
            f"blocked: {self.blocked}".join(
                ["\n" + str(p) for p in self.characters])
        return message

    def update_game_state(self, player_role):
        """
            representation of the global state of the game.
        """
        self.characters_display = [character.display() for character in
                                   self.characters]
        # Todo: should be removed
        self.character_cards_display = [tile.display() for tile in
                                        self.character_cards]
        self.active_cards_display = [tile.display() for tile in
                                     self.active_cards]
        # update

        self.game_state = {
            "position_carlotta": self.position_carlotta,
            "exit": self.exit,
            "num_tour": self.num_tour,
            "shadow": self.shadow,
            "blocked": self.blocked,
            "characters": self.characters_display,
            # Todo: should be removed
            "character_cards": self.character_cards_display,
            "active character_cards": self.active_cards_display
        }

        if player_role == "fantom":
            self.game_state["fantom"] = self.fantom.color

        return self.game_state

    def get_next_possible_actions(self) -> int:
        print("returns action array")

    def get_action_res(self, action: int) -> int:
        print("action is action index, returns position_carlotta")