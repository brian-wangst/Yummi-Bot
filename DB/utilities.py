import sqlite3
import aiohttp
import aiofiles
import json
import os
from collections import defaultdict
from PIL import Image
import shutil


async def download_champion_info(ddragon_champion_url: str, ddragon_file_champion_name, version):
    abillity_list = []
    data = await fetch_and_save_data(ddragon_champion_url,ddragon_file_champion_name)
    champion_data = json.loads(data.decode('utf-8'))
    champion_list = list(champion_data['data'].keys())
    
    await download_champion_json(champion_list, version)
    champion_abillity_map, champion_key_list = get_champion_abillity_map()
    for champion_name in champion_abillity_map.keys():
        for key, value in champion_abillity_map[champion_name].items():
            if key in ["Q", "W", "E", "R"]:
                abillity_name = value["image_name"].split(".")[0]
                abillity_list.append([f"https://ddragon.leagueoflegends.com/cdn/14.7.1/img/spell/{value["image_name"]}", abillity_name])
    await download_images(abillity_list, "champion_images")
    return champion_abillity_map, champion_key_list


async def download_items_info(ddragon_file_item_name: str, ddragon_item_url: str, version: str):
    url_list = []
    data = await fetch_and_save_data(ddragon_item_url, ddragon_file_item_name)
    data = json.loads(str(data, 'utf-8'))
    item_data = data["data"]
    for key in item_data.keys():
        item_id = key
        url_list.append([f"https://ddragon.leagueoflegends.com/cdn/{version}/img/item/{item_id}.png", item_id])

    await download_images(url_list, "item_images")


async def download_champion_json(champion_list: list, version):
    create_directory("championinfo")
    for champion in champion_list:
        champion = ''.join(filter(str.isalnum, champion)) 
        url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion/{champion}.json"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(os.path.join(os.path.abspath(os.curdir), "championinfo", f"{champion}.json"), mode='wb')
                    await f.write(await resp.read())
                    await f.close()

async def download_rune_info(ddragon_runes_url: str, ddragon_file_runes_name: str, version: str):
    url_list = []
    data = await fetch_and_save_data(ddragon_runes_url, ddragon_file_runes_name)
    rune_data = json.loads(str(data, 'utf-8'))
    base_url = f"https://ddragon.leagueoflegends.com/cdn/img"
    for item in rune_data:
        outer_rune_list = item["slots"]
        for outer_rune_dict in outer_rune_list:
            rune_list = outer_rune_dict["runes"]
            for rune_dict in rune_list:
                if rune_dict["key"] == "PerfectTiming":
                    rune_dict["key"] = "TripleTonic"
                url_list.append([f"{base_url}/{rune_dict["icon"]}", rune_dict["key"]])

    await download_images(url_list, "rune_images")


async def download_summoner_info(ddragon_summoners_url: str, ddragon_file_summoners_name: str, version: str):
    url_list = []
    data = await fetch_and_save_data(ddragon_summoners_url, ddragon_file_summoners_name)
    data = json.loads(str(data, 'utf-8'))['data']

    for key in data.keys():
        summoner_data = data[key]
        summoner_name = summoner_data["name"]
        summoner_image = summoner_data["image"]["full"]
        url_list.append([f"https://ddragon.leagueoflegends.com/cdn/{version}/img/spell/{summoner_image}",summoner_name])

    await download_images(url_list, "summoner_images")


def get_champion_abillity_map():
    champion_dict = defaultdict(dict)
    champion_key_list = []
    champion_json_path = os.path.join(os.path.abspath(os.curdir), "championinfo")
    champion_json_names = os.listdir(champion_json_path)
    absolute_paths = [os.path.join(champion_json_path, file) for file in champion_json_names]
    
    for champion_json_ref in absolute_paths:
        with open (champion_json_ref, encoding = "utf-8") as file:
            abillity_keys = ["Q", "W", "E", "R"]
            champion_data = json.load(file)['data']
            champion_name = list(champion_data.keys())[0]
            spell_data = champion_data[champion_name]["spells"]
            champion_key = champion_data[champion_name]["key"]
            for spell, abillity_key in zip(spell_data, abillity_keys):
                ability_dict = defaultdict(dict)
                ability_dict["abillity_name"] = spell['name']
                ability_dict["image_name"] = spell['image']['full']
                champion_dict[champion_name][abillity_key] = ability_dict
            champion_key_list.append(champion_key)

    return champion_dict, champion_key_list

async def download_images(urls: list[list], directory_name):
    create_directory(directory_name)
    for url in urls:
        async with aiohttp.ClientSession() as session:
            async with session.get(url[0]) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(os.path.join(os.path.abspath(os.curdir), directory_name, f"{url[1]}.png"), mode='wb')
                    await f.write(await resp.read())
                    await f.close()


def create_directory(directory_name: str):
    if not os.path.exists(os.path.join(os.path.abspath(os.curdir), directory_name)):
        os.makedirs(os.path.join(os.path.abspath(os.curdir), directory_name))

async def fetch_and_save_data(url, file_name):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            data = await res.read()
            with open(file_name, "wb") as f:
                f.write(data)
    return data


def merge_images_horizontal(image_list: list, delimiter: str, max_width_threshold=900):
    # Add an arrow image to the beginning of the list to separate images

    image_list = intersperse(delimiter, image_list)
    images = [Image.open(x) for x in image_list]

    # Find the dimensions of the smallest image
    smallest_width = min(img.width for img in images)
    smallest_height = min(img.height for img in images)

    # Resize all images to the dimensions of the smallest image
    resized_images = []
    for img in images:
        resized_img = img.resize((smallest_width, smallest_height), Image.LANCZOS)
        resized_images.append(resized_img)

    # Calculate total width and maximum height
    total_width = sum(smallest_width for _ in resized_images)
    max_height = smallest_height * ((len(resized_images) - 1) // (max_width_threshold // smallest_width) + 1)

    # Create a new blank image with the calculated dimensions and black background
    new_im = Image.new('RGB', (max_width_threshold, max_height), color='black')

    # Paste resized images into the new image
    x_offset = 0
    y_offset = 0
    for im in resized_images:
        if x_offset + smallest_width > max_width_threshold:  # Check if adding the image would exceed max_width_threshold
            x_offset = 0  # Start from the beginning of the next line
            y_offset += smallest_height  # Move to the next line

        new_im.paste(im, (x_offset, y_offset))
        x_offset += smallest_width

    return new_im


def intersperse(word,your_list):
    x = [j for i in your_list for j in [i,word]]
    x.pop()
    return x

def merge_images_vertical(image_list: list):
    imgs = image_list

    # If you're using an older version of Pillow, you might have to use .size[0] instead of .width
    # and later on, .size[1] instead of .height
    min_img_width = min(i.width for i in imgs)

    total_height = 0
    for i, img in enumerate(imgs):
        # If the image is larger than the minimum width, resize it
        if img.width > min_img_width:
            imgs[i] = img.resize((min_img_width, int(img.height / img.width * min_img_width)), Image.ANTIALIAS)
        total_height += imgs[i].height

    # I have picked the mode of the first image to be generic. You may have other ideas
    # Now that we know the total height of all of the resized images, we know the height of our final image
    img_merge = Image.new(imgs[0].mode, (min_img_width, total_height))
    y = 0
    for img in imgs:
        img_merge.paste(img, (0, y))
        y += img.height

    return img_merge


def delete_past_setup():
    item_image_folder_loc = os.path.join(os.path.abspath(os.curdir), "item_images")
    champion_image_folder_loc = os.path.join(os.path.abspath(os.curdir), "champion_images")
    champion_info_folder_loc = os.path.join(os.path.abspath(os.curdir), "championinfo")
    rune_image_folder_loc = os.path.join(os.path.abspath(os.curdir), "rune_images")
    summoner_image_folder_loc = os.path.join(os.path.abspath(os.curdir), "summoner_images")
    try:
        shutil.rmtree(item_image_folder_loc)
    except:
        pass
    try:
        shutil.rmtree(champion_image_folder_loc)
    except:
        pass
    try:
        shutil.rmtree(champion_info_folder_loc)
    except:
        pass
    try:
        shutil.rmtree(rune_image_folder_loc)
    except:
        pass
    try:
        shutil.rmtree(summoner_image_folder_loc)
    except:
        pass
    con = sqlite3.connect("League.db")
    cur = con.cursor()
    cur.execute("""DELETE FROM Items""")
    cur.execute("""DELETE FROM CHAMPION_CODES""")
    cur.execute("""DELETE FROM Runes""")
    cur.execute("""DELETE FROM Summoners""")
    con.commit()
    con.close()
