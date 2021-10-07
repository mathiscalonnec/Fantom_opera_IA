from test_src.globals import passages, pink_passages, colors


def get_current_score_from_game_state(game_state):
    return game_state["position_carlotta"]


def get_shadow_from_game_state(game_state):
    return game_state["shadow"]


def get_blocked_from_game_state(game_state):
    return game_state["blocked"]


def get_fantom_from_game_state(game_state) -> list:
    return game_state["fantom"]


def get_characters_from_game_state(game_state):
    return game_state["characters"]


def get_suspects_from_game_state(game_state):
    suspects = []

    for character in game_state["characters"]:
        if character["suspect"]:
            suspects.append(character)
    return suspects


def get_active_characters_from_game_state(game_state):
    return game_state["active character_cards"]


def get_blocked_characters_from_game_state(game_state):
    return game_state["blocked"]


def get_character_by_color(game_state, color):
    target = {}
    characters = get_characters_from_game_state(game_state)
    for character in characters:
        if character["color"] == color:
            target = character
            break
    return target


def get_characters_by_position(game_state, position):
    targets = []
    for character in get_characters_from_game_state(game_state):
        if character["position"] == position:
            targets.append(character)
    return targets


# Took two next funcs from base src
def get_adjacent_positions_from_position(position, charact, game_state):
        if charact["color"] == "pink":
            active_passages = pink_passages
        else:
            active_passages = passages
        return [room for room in active_passages[position] if set([room, position]) != set(get_blocked_characters_from_game_state(game_state))]


def is_character_alone(game_state, color) -> bool:
    character = get_character_by_color(game_state, color)
    nb = len(get_characters_by_position(game_state, character["position"]))

    return True if nb == 1 else False


def is_character_in_shadow(game_state, color):
    character = get_character_by_color(game_state, color)

    return character["position"] == get_shadow_from_game_state(game_state)


def update_list_with_character(character, c_list: list) -> list:
    character_index = next(i for i in range(len(c_list)) if c_list[i]["color"] == character["color"])
    c_list[character_index] = character
    
    return c_list


def update_game_state_with_characters(characters: list, game_state):
    updated_characters = get_characters_from_game_state(game_state)
    for c in characters:
        updated_characters = update_list_with_character(c, updated_characters)
    game_state["characters"] = updated_characters

    return game_state


def calculate_score(game_state):
    score = get_current_score_from_game_state(game_state)
    fantom = get_character_by_color(game_state, get_fantom_from_game_state(game_state))
    suspects = get_suspects_from_game_state(game_state)
    fantom_is_alone = is_character_alone(game_state, fantom["color"])

    if fantom["position"] == get_shadow_from_game_state(game_state) or fantom_is_alone:
        # Fantom is alone or in the shadow / The Fantom shouts (score +1)
        score += 1
        for suspect in suspects:
            if is_character_alone(game_state, suspect["color"]):
                # Suspect alone (score +1)
                score += 1
                continue
            if is_character_in_shadow(game_state, suspect["color"]):
                # Suspect in the shadow (score +1)
                score += 1
    else:
        # Fantom in a group
        for suspect in suspects:
            if not is_character_alone(game_state, suspect["color"]) \
                    and not is_character_in_shadow(game_state, suspect["color"]):
                # Suspect is not alone and not in the shadow / in a group (score +1)
                score += 1

    return score


def update_game_state_suspects(game_state):
    fantom = get_character_by_color(game_state, get_fantom_from_game_state(game_state))
    suspects = get_suspects_from_game_state(game_state)
    fantom_is_alone = is_character_alone(game_state, fantom["color"])

    if fantom["position"] == get_shadow_from_game_state(game_state) or fantom_is_alone:
        for suspect in suspects:
            if not is_character_alone(game_state, suspect["color"]) \
                    and not is_character_in_shadow(game_state, suspect["color"]):
                for character in get_characters_from_game_state(game_state):
                    if suspect["color"] == character["color"]:
                        character["suspect"] = False
                        break
    else:
        for suspect in suspects:
            if is_character_alone(game_state, suspect["color"]):
                for character in get_characters_from_game_state(game_state):
                    if suspect["color"] == character["color"]:
                        character["suspect"] = False
                        break
                continue
            if is_character_in_shadow(game_state, suspect["color"]):
                for character in get_characters_from_game_state(game_state):
                    if suspect["color"] == character["color"]:
                        character["suspect"] = False
                        break
    return game_state