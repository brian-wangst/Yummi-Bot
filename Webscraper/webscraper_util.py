def format_abillities(abillity_order: list):
    key_mapper = {0:"Q", 1:"W", 2:"E", 3:"R"}
    abillity_order.sort(key = lambda x: x[0])
    for abillity in abillity_order:
        abillity[1] = key_mapper[abillity[1]]
    
    abillity_order = [item[1] for item in abillity_order]
    return abillity_order
    
def format_runes(runes: list):
    res = []
    stat_modifier_map = {
        0: {0: "Adaptive Force", 1: "Attack Speed", 2: "Abillity Haste"},
        1: {0: "Adaptive Force", 1: "Movement Speed", 2: "Health"},
        2: {0: "Health", 1: "Tenacity", 2: "Health Scaling"}
    }

    stat_modifiers = runes[6:]
    for i in range(len(stat_modifiers)):
        stat_modifiers[i] = stat_modifier_map[i][stat_modifiers[i]]
    
    res.append(runes[:4])
    res.append(runes[4:6])
    res.append(stat_modifiers)
    return res

def format_stat_modifiers(stat_modifiers: list):
    message = "Take these modifiers: "
    combined_modifiers = ", ".join(stat_modifiers)
    return message + combined_modifiers