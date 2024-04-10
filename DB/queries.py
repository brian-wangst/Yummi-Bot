import sqlite3
import aiohttp
import json
import os
from DB import models, utilities, database
from collections import Counter


DATABASE_PATH = "League.db"

async def update_ddragon_and_db():
    database.initialize_database()
    ddragon_versions_url = "https://ddragon.leagueoflegends.com/api/versions.json"
    async with aiohttp.ClientSession() as session:
        async with session.get(ddragon_versions_url) as res:
            data = await res.read()
    
    version = json.loads(data.decode('utf-8'))[0]
    ddragon_file_champion_name = f"Ddragon_Champion_{version}.json"
    ddragon_file_item_name = f"Ddragon_item_{version}.json"
    ddragon_file_runes_name = f"Ddragon_Runes_{version}.json"
    ddragon_file_summoners_name = f"Ddragon_Summoners_{version}.json"
    ddragon_file_list = [ddragon_file_champion_name, ddragon_file_item_name, ddragon_file_runes_name, ddragon_file_summoners_name]

    for file in ddragon_file_list:
        if file not in os.listdir():
            utilities.delete_past_setup()
            ddragon_base_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US"
            ddragon_champion_url = f"{ddragon_base_url}/champion.json"
            ddragon_item_url = f"{ddragon_base_url}/item.json"
            ddragon_runes_url = f"{ddragon_base_url}/runesReforged.json"
            ddragon_summoners_url = f"{ddragon_base_url}/summoner.json"
            
            champion_abillity_map, champion_key_list = await utilities.download_champion_info(ddragon_champion_url, ddragon_file_champion_name, version)
            load_champion_codes_db(champion_abillity_map, champion_key_list)
            
            await utilities.download_items_info(ddragon_file_item_name, ddragon_item_url, version)
            load_items_db(ddragon_file_item_name)

            await utilities.download_rune_info(ddragon_runes_url, ddragon_file_runes_name, version)
            load_runes_db(ddragon_file_runes_name)

            await utilities.download_summoner_info(ddragon_summoners_url, ddragon_file_summoners_name, version)
            load_summoners_db(ddragon_file_summoners_name)

            # break
        
    return "Setup Complete"
    

def load_champion_codes_db(champion_abillity_map: dict, champion_key_list: list):
    con = sqlite3.connect("League.db")
    cur = con.cursor()

    for idx, (key, value) in enumerate(champion_abillity_map.items()):
        champion_code = models.ChampionCode(id=champion_key_list[idx], champion_name=key.lower(), champion_abillities=json.dumps(value))
        select_query = """SELECT * FROM Champion_Codes WHERE id= ? AND champion_name= ?"""

        cur.execute(select_query, (champion_code.id, champion_code.champion_name))
        res = cur.fetchone()

        if not res:
            cur.execute('''INSERT INTO Champion_Codes(id, champion_name,  champion_abillities) VALUES(?,?,?)''', (champion_code.id, champion_code.champion_name, champion_code.champion_abillities))
            con.commit()

    con.close()


def load_items_db(file_name: str):
    con = sqlite3.connect("League.db")
    cur = con.cursor()

    with open(file_name, encoding='utf-8') as f:
        data = json.load(f)
        item_data = data["data"]
        for key, value in item_data.items():
            item = models.Item(id=key, item_name=value['name'], local_ref=os.path.join(os.path.abspath(os.curdir), "item_images", value["image"]["full"]))
            select_query = """SELECT * FROM Items WHERE id= ?"""

            cur.execute(select_query, (item.id,))
            res = cur.fetchone()

            if not res:
                cur.execute('''INSERT INTO Items(Item_Name, ID, Local_Ref) VALUES(?,?,?)''', (item.item_name, item.id, item.local_ref))
                con.commit()

    con.close()

def load_runes_db(file_name: str):
    con = sqlite3.connect("League.db")
    cur = con.cursor()

    with open(file_name, encoding='utf-8') as f:
        data = json.load(f)
        for item in data:
            outer_rune_list = item["slots"]
            for outer_rune_dict in outer_rune_list:
                rune_list = outer_rune_dict["runes"]
                for rune_dict in rune_list:
                    if rune_dict["key"] == "PerfectTiming":
                        rune_dict["key"] = "TripleTonic"
                    rune = models.Runes(id = rune_dict["id"], rune_name= rune_dict["name"], local_ref=os.path.join(os.path.abspath(os.curdir), "rune_images", f"{rune_dict["key"]}.png"))
                    select_query = """SELECT * FROM Items WHERE id= ?"""                    

                    cur.execute(select_query, (rune.id,))
                    res = cur.fetchone()

                    if not res:
                        cur.execute('''INSERT INTO Runes(Rune_Name, ID, Local_Ref) VALUES(?,?,?)''', (rune.rune_name, rune.id, rune.local_ref))
                        con.commit()

    con.close()

def load_summoners_db(file_name: str):
    con = sqlite3.connect("League.db")
    cur = con.cursor()
    con.commit()

    with open(file_name, encoding='utf-8') as f:
        data = json.load(f)["data"]
        for key in data.keys():
            summoner_data = data[key]
            Summoner = models.Summoners(id = summoner_data["id"], summoner_name = summoner_data["name"], local_ref = os.path.join(os.path.abspath(os.curdir), "summoner_images", f"{summoner_data["name"]}.png"))
            select_query = """SELECT * FROM Summoners WHERE id= ?"""  

            cur.execute(select_query, (Summoner.id,))
            res = cur.fetchone()

            if not res:
                cur.execute('''INSERT INTO Summoners(Summoner_Name, ID, Local_Ref) VALUES(?,?,?)''', (Summoner.summoner_name, Summoner.id, Summoner.local_ref))
                con.commit()

    con.close()

def load_users_db(discord_id: str, discord_name: str, game_name: str, tag_line: str):
    con = sqlite3.connect("League.db")
    cur = con.cursor()

    select_query = """SELECT * FROM Users WHERE Discord_id= ?"""

    cur.execute(select_query, (discord_id,) )
    res = cur.fetchone()

    if not res:
        cur.execute('''INSERT INTO Users(Discord_id, Discord_name, Game_name, Tag_line) VALUES(?,?,?,?)''', (discord_id, discord_name, game_name, tag_line))
    else:
        cur.execute('''UPDATE Users SET Discord_name = ?, Game_name = ?, tag_line = ? WHERE Discord_id = ?''', (discord_name, game_name, tag_line, discord_id))
        
    con.commit()
    con.close()


async def get_abillity_images(abillity_order: list, champion_name: str):
    con = sqlite3.connect("League.db")
    cur = con.cursor()
    select_query = """SELECT champion_abillities FROM CHAMPION_CODES WHERE champion_name= ? """
    cur.execute(select_query, (champion_name,))
    res = cur.fetchone()
    con.close()
    abillity_max_counter = Counter(abillity_order)
    image_list = []
    simplified_image_list = []

    if res:
        abillity_map, = res
        abillity_map = json.loads(abillity_map)
        champion_images_path = os.path.join(os.path.abspath(os.curdir), "champion_images")

        for abillity in abillity_order:
            image_list.append(os.path.join(champion_images_path, abillity_map[abillity]["image_name"]))
            abillity_max_counter[abillity]-=1
            if abillity_max_counter[abillity] == 0 and abillity != "R":      #Don't include ultimate abillities in simplifed picture
                simplified_image_list.append(os.path.join(champion_images_path, abillity_map[abillity]["image_name"]))
                abillity_max_counter.pop(abillity)

        ordered_image = utilities.merge_images_horizontal(image_list, R"C:\Users\Brian\Desktop\bot\static_images\arrow.jpg")
        simplified_ordered_image = utilities.merge_images_horizontal(simplified_image_list, R"C:\Users\Brian\Desktop\bot\static_images\arrow.jpg")
        return utilities.merge_images_vertical([ordered_image, simplified_ordered_image])

async def get_item_images(item_order: list):
    con = sqlite3.connect("League.db")
    cur = con.cursor()
    select_query = """SELECT Local_Ref FROM Items WHERE Item_Name = ? """
    item_image_list = []
    
    for idx, items in enumerate(item_order):
        item_list = []
        if idx == 0:
            delimiter = R"C:\Users\Brian\Desktop\bot\static_images\arrow.jpg"
        else:
            delimiter = R"C:\Users\Brian\Desktop\bot\static_images\or.jpg"
        for item in items:
            cur.execute(select_query, (item,))
            res = cur.fetchone()
            if res:
                item_path, = res
                item_list.append(item_path)

        item_image_list.append(utilities.merge_images_horizontal(item_list, delimiter))

    return utilities.merge_images_vertical(item_image_list)

async def get_rune_image(rune_list: list):
    con = sqlite3.connect("League.db")
    cur = con.cursor()
    delimiter = R"C:\Users\Brian\Desktop\bot\static_images\arrow.jpg"
    select_query = """SELECT Local_Ref FROM Runes WHERE Rune_Name = ? """
    rune_image_list = []
    
    for runes in rune_list:
        rune_list = []
        for rune in runes:
            cur.execute(select_query, (rune,))
            res = cur.fetchone()
            if res:
                rune_path, = res
                rune_list.append(rune_path)

        rune_image_list.append(utilities.merge_images_horizontal(rune_list, delimiter))

    return utilities.merge_images_vertical(rune_image_list)

async def get_summoner_image(summoner_list: list):
    con = sqlite3.connect("League.db")
    cur = con.cursor()
    delimiter = R"C:\Users\Brian\Desktop\bot\static_images\arrow.jpg"
    select_query = """SELECT Local_Ref FROM Summoners WHERE Summoner_name = ? """
    summoner_image_list = []
    
    for summoner in summoner_list:
        cur.execute(select_query, (summoner,))
        res = cur.fetchone()
        if res:
            summoner_path, = res
            summoner_image_list.append(summoner_path)

    return utilities.merge_images_horizontal(summoner_image_list, delimiter)


def check_user_db(game_name: str):
    con = sqlite3.connect("League.db")
    cur = con.cursor()
    select_query = """SELECT discord_id FROM Users WHERE Game_name = ?"""  
    cur.execute(select_query, (game_name,))
    res = cur.fetchone()

    if res:
        print("found")
        discord_id, = res
        return discord_id
    return None

def get_champion_name(champion_id: int):
    con = sqlite3.connect("League.db")
    cur = con.cursor()
    select_query = """SELECT champion_name FROM CHAMPION_CODES WHERE id = ?"""
    cur.execute(select_query, (str(champion_id),))
    res = cur.fetchone()

    if res:
        champion_nanme, = res
        return champion_nanme
    return None

