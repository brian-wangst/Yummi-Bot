class ChampionCode:
    def __init__(self, id, champion_name, champion_abillities):
        self.id = id
        self.champion_name = champion_name
        self.champion_abillities = champion_abillities

    def __repr__(self):
        return f'<ChampionCode(id={self.id}, champion_name={self.champion_name}, champion_abillities={self.champion_abillities})>'


class Item:
    def __init__(self, id, item_name, local_ref):
        self.id = id
        self.item_name = item_name
        self.local_ref = local_ref

    def __repr__(self):
        return f'<Item(id={self.id}, item_name={self.item_name}, local_ref={self.local_ref})>'


class Runes:
    def __init__(self, id, rune_name, local_ref):
        self.id = id
        self.rune_name = rune_name
        self.local_ref = local_ref

    def __repr__(self):
        return f'<Item(id={self.id}, item_name={self.rune_name}, local_ref={self.local_ref})>'


class Summoners:
    def __init__(self, id, summoner_name, local_ref):
        self.id = id
        self.summoner_name = summoner_name
        self.local_ref = local_ref

    def __repr__(self):
        return f'<Item(id={self.id}, item_name={self.summoner_name}, local_ref={self.local_ref})>'


class User:
    def __init__(self, discord_id, discord_name, game_name, tag_line):
        self.discord_id = discord_id
        self.discord_name = discord_name
        self.game_name = game_name
        self.tag_line = tag_line

    def __repr__(self):
        return f'<Item(id={self.discord_id}, discord_name={self.discord_name}, game_name={self.game_name}, tag_line={self.tag_line})>'
