import settings
import discord
from discord.ext import commands
import RiotAPI.riotapi as riotapi
import RiotAPI.tools as tools
from DB import queries
from io import BytesIO
from PIL import Image
import discord_utils


def run():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    intents.guilds = True
    bot = commands.Bot(command_prefix="!", intents=intents)
    @bot.event
    async def on_ready():
        await send_message_to_channel(bot, await queries.update_ddragon_and_db())

    @bot.command()
    async def get_opponent_info(ctx, *args) -> str:
        """Retrieve the Json string from a in game matchup"""
        if not isinstance(ctx.channel, discord.DMChannel):
            puuid = await riotapi.get_league_puuid(args)
            ingame_info = await riotapi.get_ingame_analysis(puuid)
            my_team_data, enemy_team_data = tools.get_teams(ingame_info, puuid)
            discord_utils.get_roles(my_team_data, enemy_team_data)
            for player in my_team_data:
                user_id = queries.check_user_db(player.game_name)
                if user_id:
                    for enemy_player in enemy_team_data:
                        if player.role == enemy_player.role:
                            champion_one = queries.get_champion_name(player.champion_id)
                            champion_two = queries.get_champion_name(enemy_player.champion_id)
                            if champion_one and champion_two:
                                build_flag = await discord_utils.ask_user_for_buildflag(ctx, bot)
                                image_list = await discord_utils.get_build_images(champion_one, champion_two, player.role, build_flag)
                                for image in image_list:
                                    await send_image_to_player(user_id, image)
        else:
           return await ctx.send(f"Please use this command in text channels only.")


    @bot.command()
    async def add_user(ctx, *args):
        if isinstance(ctx.channel, discord.DMChannel):
            discord_id, discord_name, game_name, tag_line = await discord_utils.add_user_args_handler(ctx, bot, discord.DMChannel)
            queries.load_users_db(str(discord_id), discord_name, game_name, tag_line)
            await send_message_to_author(ctx, "User succesfuly added")
        else:
            await send_message_to_author(ctx, "This command but be used in a DM with League Bot")


    @bot.command()
    async def get_matchup(ctx, *args):
        if isinstance(ctx.channel, discord.DMChannel):
            champion_one, champion_two, position = discord_utils.get_matchup_args_handler(args)
            build_flag = await discord_utils.ask_user_for_buildflag(ctx, bot)
            image_list = await discord_utils.get_build_images(champion_one, champion_two, position, build_flag)
            for image in image_list:
                await send_images_to_author(ctx, image)
        else:
            await send_message_to_author(ctx, "This command must be used in a DM with League Bot")
        
    async def send_images_to_author(ctx, *images: Image.Image):
        for i, img in enumerate(images):
        # Convert PIL image to BytesIO object
            img_bytes = BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)

            # Send the image as a file
            file = discord.File(img_bytes, filename=f'image{i + 1}.png')
            await ctx.author.send(file=file)

    async def send_image_to_player(user_id, *images: Image.Image):
        # Fetch the user object using the user_id
        user = await bot.fetch_user(user_id)

        # Send images individually
        for i, img in enumerate(images):
            # Convert PIL image to BytesIO object
            img_bytes = BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)

            # Send the image as a file
            file = discord.File(img_bytes, filename=f'image{i + 1}.png')
            await user.send(file=file)



    async def send_message_to_channel(ctx, message: str):
        channel = ctx.get_channel(1220118670399770758)
        
        await channel.send(message)
        
    async def send_message_to_author(ctx, message: str):
        await ctx.author.send(message)

    bot.run(settings.DISCORD_API_SECRET)



if __name__ == "__main__":
    run()
