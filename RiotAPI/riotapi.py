import aiohttp
import settings
from RiotAPI import tools


async def get_league_puuid(args) -> str:
    """Return the puuid associated with the users game_name and tag_line"""
    args_list = list(args)
    game_name = " ".join(args_list[:-1])
    tag_line = args_list[-1]
    puuid_url = "https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id"
    completed_puuid_url = f"{puuid_url}/{game_name}/{tag_line}"

    header = {
        "X-Riot-Token": settings.LEAGUE_API_SECRET
    }
    
    async with aiohttp.ClientSession(headers=header) as session:
        async with session.get(completed_puuid_url) as res:
            data = await res.json()
            return data["puuid"]
        

async def get_ingame_analysis(puuid: str) -> str:
    """Return the json structure with in game analysis of the current game"""
    url = "https://na1.api.riotgames.com/lol/spectator/v5/active-games/by-summoner"
    completed_current_game_url = f"{url}/{puuid}"

    header = {
        "X-Riot-Token": settings.LEAGUE_API_SECRET
    }
    
    async with aiohttp.ClientSession(headers=header) as session:
        async with session.get(completed_current_game_url) as res:
            data = await res.json()
            return data

async def get_champion_mastery(player_list: list[tools.LivePlayer]) -> str:
    """Returns the champion mastery a player has on a champion"""
    header = {
        "X-Riot-Token": settings.LEAGUE_API_SECRET
    }

    for player in player_list:
        champion_mastery_url = f"https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{player.puuid}/by-champion/{player.champion_id}"
        async with aiohttp.ClientSession(headers=header) as session:
            async with session.get(champion_mastery_url) as res:
                data = await res.json()
                player.champion_mastery = data["championPoints"]
            


