from bs4 import BeautifulSoup
from ordered_set import OrderedSet
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from Webscraper import webscraper_util
 
def get_build_data(champion_one: str, champion_two: str, position: str, build_toggle: bool):
    options = Options()
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--allow-running-insecure-content")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)

    url = f"https://lolalytics.com/lol/{champion_one}/vs/{champion_two}/build/?lane={position}&vslane={position}"
    driver.get(url)

    toggle_responses = ['common', "Common"]
    if build_toggle in toggle_responses:
        button = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//div[@class='flex-auto text-center text-xs bg-[#214753] hover:bg-[#57a5bd] border border-[#060d0f] py-2 select-none cursor-pointer']"))
        )
        button.click()
        time.sleep(0.5)

    html = driver.page_source
    global soup
    soup = BeautifulSoup(html, 'html.parser')

    abillity_order = webscraper_util.format_abillities(get_abillity_order())
    runes = webscraper_util.format_runes(get_runes())
    item_build = get_items()
    stat_modifers = (webscraper_util.format_stat_modifiers(runes[-1]))
    summoners = get_summoners()

    return abillity_order, runes, item_build, stat_modifers, summoners
    
def get_abillity_order():
    res = []
    last_order_seen = 0
    abillity_id = 0
    items = soup.find_all('div', class_="m-auto mb-[2px] flex w-[317px]")
    for idx, item in enumerate(items):
        div_list = item.find_all("div", {"class": "mr-[1px] h-[28px] w-[18px] border border-[#30687a]"})
        for result in div_list:
            if result.get_text():
                res.append([int(result.get_text()), idx])

    return res
    
def get_keystone_rune():
    items = soup.find_all('div', class_="flex justify-between")
    for item in items:
        span_elments = item.find_all('span')
        for span_element in span_elments:
            img_element = span_element.find('img')
            if "grayscale" not in img_element.get('class'):
                return img_element.get('alt')
            
def get_runes():
    rune_list = []
    rune_list.append(get_keystone_rune())
    count = 0
    items = soup.find_all('div', class_="flex justify-between mb-1")
    for item in items:
        span_elments = item.find_all('span')
        for span_element in span_elments:
            img_element = span_element.find('img')
            if img_element.get('alt') == 'statmod':
                if "grayscale" not in img_element.get('class'):
                    rune_list.append(count)
                    count = 0
                    break
                else:
                    count+=1
            else:
                if "grayscale" not in img_element.get('class'):
                    rune_list.append(img_element.get('alt'))
    return rune_list

def get_items():
    item_list = []
    items = soup.find_all('div', class_ = "mb-2 basis-1/2 md:basis-1/3 lg:basis-auto")
    for item in items:
        item_elements = item.find_all('div', class_= 'flex justify-center')
        item_set = OrderedSet()
        for item_element in item_elements:
            img_element = item_element.find('img')
            item_set.add(img_element.get('alt'))
        item_list.append(list(item_set))

    return item_list

def get_summoners():
    summoner_list = []
    items = soup.find_all('div', class_="flex justify-center gap-2")
    for item in items:
        span_elments = item.find_all('span')
        for span_element in span_elments:
            img_element = span_element.find('img')
            summoner_list.append(img_element.get('alt'))

    return summoner_list
