class LivePlayer:
    def __init__(self, puuid: str, champion_id: str, game_name: str, summoner_spell1: str, summoner_spell2: str):
        self.puuid = str(puuid)
        self.champion_id = str(champion_id)
        self.game_name = game_name
        self.summoner_spell1 = str(summoner_spell1)
        self.summoner_spell2 = str(summoner_spell2)
        self.champion_mastery = None
        self.role = None

def get_teams(ingame_info: dict, puuid: str):
    my_team = []
    enemy_team = []
    team_id = 0

    player_info = ingame_info["participants"]
    for item in player_info:
        if item["puuid"] == puuid:
            team_id = item["teamId"]
    
    for item in player_info:
        summoner_spell1 = item["spell1Id"]
        summoner_spell2 = item["spell2Id"]
        if item["teamId"] == team_id:
            my_team.append(LivePlayer(item["puuid"], item["championId"], item["summonerName"], summoner_spell1, summoner_spell2))
        else:
            enemy_team.append(LivePlayer(item["puuid"], item["championId"], item["summonerName"], summoner_spell1, summoner_spell2))
        
    return (my_team, enemy_team)

def get_matchup_names(args) -> str:
    args_list = list(args)
    champion_one = ''.join([i for i in args_list[0] if i.isalpha()])
    champion_two = ''.join([i for i in args_list[1] if i.isalpha()])
    return champion_one, champion_two


