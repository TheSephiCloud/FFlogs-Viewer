# Copyright (C) 2019 Mika Thesephicloud on Lich | <https://github.com/TheSephiCloud>.
#
# This file is part of FFlogs-Viewer.
#
# FFlogs-Viewer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# FFlogs-Viewer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with FFlogs-Viewer.  If not, see <https://www.gnu.org/licenses/>.

import asyncio
import concurrent.futures
import json
from operator import itemgetter
import configparser
import requests as req
import os

wd = os.getcwd()
config = configparser.ConfigParser()
try:
    config.read(wd + r"/pics/data.ini")
    APIKey = config['Settings']['API_key']
except KeyError:
    print("KeyError, Key not found in the file")
    API_key = ""


def get_link(link):
    data = req.get(link)
    data = json.loads(data.text)
    return data


async def get_data(links):
    datalist = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        future_to_url = {executor.submit(get_link, url): url for url in links}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                datalist.append(future.result())
            except Exception as exc:
                print("Exception:", exc, url)
    return datalist


def get_zones(difficulty):
    strings = ("Extreme", "Savage", "Bahamut", "Refrain")
    link = f"https://www.fflogs.com/v1/zones?api_key={APIKey}"
    story_zones, story_ids, zone_list_story, difficult_zones, difficult_ids, zone_list_difficult = [], [], [], [], [], []
    data = get_link(link)
    for zone in data:
        for string in strings:
            try:
                if string in zone["name"]:
                    zone_list_difficult.append(zone["name"])
                    for encounter in zone["encounters"]:
                        difficult_zones.append((zone["id"], encounter["id"], encounter["name"]))
                        if not zone["id"] in difficult_ids:
                            difficult_ids.append(zone["id"])
                    break
            except TypeError:
                print("Please enter a valid API Key")
        else:
            zone_list_story.append(zone["name"])
            for encounter in zone["encounters"]:
                story_zones.append((zone["id"], encounter["id"], encounter["name"]))
                if not zone["id"] in story_ids:
                    story_ids.append(zone["id"])
    if difficulty:
        return difficult_zones, difficult_ids, zone_list_difficult
    elif not difficulty:
        return story_zones, story_ids, zone_list_story


def request_percentiles(name, server, zoneids, region):
    percentiles = []
    linklist = []
    for encounter in zoneids:
        link = f"https://www.fflogs.com/v1/rankings/character/{name}/{server}/{region}?zone={encounter}&partition=1&timeframe=historical&api_key={APIKey}"
        linklist.append(link)
    dataresults = asyncio.run(get_data(linklist))
    for sdata in dataresults:
        for classes in sdata:
            percentiles.append((classes["spec"], classes["percentile"], classes["encounterID"], classes["encounterName"], classes["reportID"], classes["total"]))
    return percentiles


def sort_key_zones(result, zones):
    for zone in zones:
        if result[2] == zone[1]:
            return zone[0]


def finalize_percentiles(name, zones, ids, region="EU"):
    server = name[name.find("@")+1:]
    name = name[0:len(name)-len(server)-1]
    name = name.replace(" ", "%20")
    percentile = request_percentiles(name, server, ids, region)
    percentile = sorted(percentile, key=itemgetter(2))
    percentile = sorted(percentile, key=lambda res: sort_key_zones(res, zones))
    return percentile


def process_name_and_paste(paste):
    #  dc_list = ("Chaos", "Light", "Aether", "Primal", "Elemental", "Gaia", "Mana")
    region_list = ("EU", "EU", "US", "US", "JP", "JP", "JP")
    server_list = []
    name_list = []
    server_list.append(("Cerberus", "Louisoix", "Moogle", "Omega", "Ragnarok"))
    server_list.append(("Lich", "Odin", "Phoenix", "Shiva", "Zodiark"))
    server_list.append(("Adamantoise", "Balmung", "Cactuar", "Coeurl", "Faerie", "Gilgamesh", "Goblin", "Jenova", "Mateus", "Midgardsormr", "Sargatanas", "Siren", "Zalera"))
    server_list.append(("Behemoth", "Brynhildr", "Diabolos", "Excalibur", "Exodus", "Famfrit", "Hyperion", "Lamia", "Leviathan", "Malboro", "Ultros"))
    server_list.append(("Aegis", "Atomos", "Carbuncle", "Garuda", "Gungnir", "Kujata", "Ramuh", "Tonberry", "Typhon", "Unicorn"))
    server_list.append(("Alexander", "Bahamut", "Durandal", "Fenrir", "Ifrit", "Ridill", "Tiamat", "Ultima", "Valefor", "Yojimbo", "Zeromus"))
    server_list.append(("Anima", "Asura", "Belias", "Chocobo", "Hades", "Ixion", "Mandragora", "Masamune", "Pandaemonium", "Shinryu", "Titan"))
    for dc_num, datacenter in enumerate(server_list):
        for server in datacenter:
            for i in range(paste.count("@" + server)):
                if paste.find(server) >= 0:
                    at_position = paste.find("@" + server)
                    second_space = paste.rfind(" ", 0, at_position)
                    name_start = [paste.rfind(" ", 0, second_space) + 1, paste.rfind("]", 0, second_space) + 1]
                    name_start = max(name_start)
                    name_end = at_position + len(server) + 1
                    name_list.append((paste[name_start:name_end], region_list[dc_num]))
                    paste = paste.replace(name_list[-1][0], "")
            for i in range(paste.count(server)):
                if paste.find(server) >= 0:
                    server_start = paste.find(server)
                    second_space = paste.rfind(" ", 0, server_start)
                    name_start = [paste.rfind(" ", 0, second_space) + 1, paste.rfind("]", 0, second_space) + 1]
                    name_start = max(name_start)
                    name_list.append((paste[name_start:server_start] + "@" + server, region_list[dc_num]))
                    paste = paste.replace(paste[name_start:server_start + len(server) + 1], "")
    return name_list
