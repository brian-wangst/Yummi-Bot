from RiotAPI import tools
import asyncio
from DB import queries
import roleidentification
from Webscraper import webscraper 

def get_matchup_args_handler(args):
    champion_one, champion_two = tools.get_matchup_names(args)
    position = args[-1]

    return champion_one, champion_two, position


async def add_user_args_handler(ctx, bot, channel_obj):
    user = ctx.author
    user_id = ctx.author.id
    await user.send("Please input Discord name:")
    
    def check(msg):
         return msg.author == ctx.author and isinstance(ctx.channel, channel_obj)

    try:
        # Wait for the user's response
        response1 = await bot.wait_for('message', check=check, timeout=60)
        discord_name = response1.content

        await user.send("Please input League name:")
        response2 = await bot.wait_for('message', check=check, timeout=60)
        league_name = response2.content

        await user.send("Please input tag line:")
        response3 = await bot.wait_for('message', check=check, timeout=60)
        tag_line = response3.content
        if tag_line[0] == '#':
            tag_line = tag_line[1:]
        

        # Send a direct message to the user with the collected information
        await user.send(f"Thank you for providing the information!\nDiscord Name: {discord_name}\nLeague Name: {league_name}\nTag Line: {tag_line}")

    except asyncio.TimeoutError:
        await user.send("You took too long to respond.")

    return user_id, discord_name, league_name, tag_line

def get_roles(my_team: list, enemy_team: list):
    my_team_ids = [int(obj.champion_id) for obj in my_team]
    enemy_team_ids = [int(obj.champion_id) for obj in enemy_team]
    champion_roles = roleidentification.pull_data()
    my_team_roles = roleidentification.get_roles(champion_roles, my_team_ids)
    enemy_team_roles = roleidentification.get_roles(champion_roles, enemy_team_ids)

    for player in my_team:
        for role, champion_id in my_team_roles.items():
            if player.champion_id == str(champion_id):
                player.role = role.lower()
                break
    
    for player in enemy_team:
        for role, champion_id in enemy_team_roles.items():
            if player.champion_id == str(champion_id):
                player.role = role.lower()
                break

async def ask_user_for_buildflag(ctx, bot):
    user = ctx.author
    channel = ctx.channel

    await channel.send("Would you like the most common build or the highest winrate build? Please type 'common' or 'winrate'.")
    
    def check(msg):
         return msg.author == user and msg.channel == channel

    try:
        # Wait for the user's response
        response = await bot.wait_for('message', check=check, timeout=60)
        build_flag = response.content.lower()

        if build_flag not in ['common', 'winrate', "Common", "Winrate"]:
            await channel.send("Invalid choice. Please type 'common' or 'winrate'.")
            return await ask_user_for_buildflag(ctx)  # Recursive call to ask again
        
        return build_flag

    except asyncio.TimeoutError:
        await channel.send("You took too long to respond.")
        return None  # Or handle the timeout error accordingly
    

async def get_build_images(champion_one: str, champion_two: str, position: str, build_flag: str):
    abillity_order, runes, item_build , stat_modifier, summoner = webscraper.get_build_data(champion_one, champion_two, position, build_flag)
    abillity_image = await queries.get_abillity_images(abillity_order, champion_one)
    item_image = await queries.get_item_images(item_build)
    rune_image = await queries.get_rune_image(runes[:2])
    summoner_image = await queries.get_summoner_image(summoner)

    return [abillity_image, item_image, rune_image, summoner_image]
    
