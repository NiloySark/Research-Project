import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import json
import re
from json.decoder import JSONDecodeError
from stringcolor import cs
import sys
import requests
import couchdb
import time

KEY_LAST_ACCOUNT_ID = 'last_account_id'

api_count = 0

""" Class Steam ID: 

Contains Bit, information for generation of the Steam ID
"""

class SteamID:
    account_id = 0
    instance = 1
    steam_2 = ''
    steam_64 = 0
    type = 1
    universe = 0

    def __init__(self, value):
        self.steam_2 = value
        match = re.match(r"^STEAM_(?P<universe>[0-4]):(?P<reminder>[0-1]):(?P<id>[0-9]{1,10})$", value)

        if not match:
            print('Incorrect STEAM ID')
        else:
            self.accountId = int(match.group('id'))
            steam32 = (self.accountId << 1) | int(match.group('reminder'))
            self.universe = int(match.group('universe'))
            if self.universe == 0:
                self.universe = 1
            self.steam_64 = (self.universe << 56) | (self.type << 52) | (self.instance << 32) | steam32

"""
Save_account_id : creates a JSON file that stores the last account ID information.

last_account_id : fetches the last account ID from the JSON to pick up from where it left off"""

def get_last_account_id():
    try:
        with open('config.json', 'r') as config_file:
            data = json.load(config_file)
            if KEY_LAST_ACCOUNT_ID in data:
                return data[KEY_LAST_ACCOUNT_ID]
            return 0
    except (FileNotFoundError, JSONDecodeError):
        return 0


def save_account_id(account_id):
    with open('config.json', 'w') as config_file:
        data = {KEY_LAST_ACCOUNT_ID: account_id}
        json.dump(data, config_file)


def generate_steam_id(account_id):
    return f'STEAM_1:1:{account_id}'

"""
Steam API has a limitation of allowing only 100 API calls per minute, the 'api_count variable keeps track of that'
"""
def start_program(account_id=0):
    global api_count
    db, db2 = init_couch_db()
    while account_id < 4294967295:
        account_id += 1
        steam_2 = generate_steam_id(account_id)
        steam_id_obj = SteamID(steam_2)
        steam_id = steam_id_obj.steam_64
        get_player_data(steam_id, db, db2)
        save_account_id(account_id)
        if api_count >= 100:
            api_count = 0
            print('waiting for a minute...')
            time.sleep(60)

""" 
initialize counchdb instances
"""
def init_couch_db():
    couch = couchdb.Server(couchIP)
    db = couch['steamids']
    db2 = couch['aussteamids']
    return db, db2

"""
create the document with the id as the Steam ID of the user
"""
def create_or_get_documents(db, steam_id):
    doc_id = str(steam_id)
    if doc_id in db:
        regular_doc = db[doc_id]
    else:
        db[doc_id] = {}
        regular_doc = db[doc_id]
    return regular_doc

"""
using the generated API make get player summary api call
"""
def get_player_data(steam_id, db, db2):
    global api_count
    print(cs(f'Fetching player data for steamid {steam_id}', '#b4d3fa'))
    url = f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={STEAM_API_KEY}&steamids={steam_id}'
    api_count += 1
    resp = requests.get(url)
    try:
        info = resp.json()['response']['players'][0]
        info.pop('communityvisibilitystate', None)
        info.pop('profilestate', None)
        info.pop('profileurl', None)
        info.pop('avatar', None)
        info.pop('avatarmedium', None)
        info.pop('avatarfull', None)
        info.pop('avatarhash', None)
        info.pop('personastate', None)
        info.pop('primaryclanid', None)
        info.pop('personastateflags', None)
        info = get_owned_games_data(steam_id, info)
        save_to_db(db, steam_id, info, db2)
    except IndexError:
        print(cs(f'Skipping {steam_id} because no data of player', '#ff0000'))

"""
with the generated Steam ID make an API call to get OWned games
"""
def get_owned_games_data(steam_id, info):
    global api_count
    print(cs(f'Fetching owned game data for steamid {steam_id}', '#b4d3fa'))
    url = f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={STEAM_API_KEY}&steamid={steam_id}'
    resp = requests.get(url)
    api_count += 1
    try:
        ownedgames = resp.json()['response']['games']
        tottime = 0
        listy = []
        for x in ownedgames:
            x.pop('playtime_windows_forever', None)
            x.pop('playtime_mac_forever', None)
            x.pop('playtime_linux_forever', None)
            tottime = tottime + x['playtime_forever']
            listy.append(x)
        info['total_playtime'] = tottime
        info['ownedgames'] = listy
    except KeyError:
        print(cs(f'Skipping {steam_id} because no data on owned games', '#ff0000'))
    return info

"""
save the collected information onto couchdb
"""
def save_to_db(db, steam_id, info, db2):
    regular_doc = create_or_get_documents(db, steam_id)
    for key in info:
        try:
            regular_doc[key] = info[key]
            db.save(regular_doc)
            print(cs(f'Saved {steam_id} to db', '#00ff00'))
        except BaseException as e:
            print(cs(f'Unable to save {steam_id} to db', '#ff0000'))
            print(sys.exc_info())
    if 'loccountrycode' in info and info['loccountrycode'] == "AU":
        aus_doc = create_or_get_documents(db2, steam_id)
        for key in info:
            try:
                aus_doc[key] = info[key]
                db2.save(aus_doc)
                print(cs(f'Saved {steam_id} to aus db', '#00ff00'))
            except BaseException as e:
                print(cs(f'Unable to save {steam_id} to AUS db', '#ff0000'))
                print(sys.exc_info())


"""
main program
the steam api key and couchdb IP's are encrypted
"""

if __name__ == '__main__':
    global  STEAM_API_KEY
    global  couchIP
    print("Please enter the password")
    password_provided = input()
    password = password_provided.encode() 
    salt = b'salt_' 
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)
    try:
        decrypted = f.decrypt(b'gAAAAABezWarvyr-225xZ7yBU9NtFfNS193l9r7zScyf8fZHKLvDKeYjfqMRGarBDHBjemul9CGgZnexlfg939DMFasQXBmXiULMxd5WKhJH9-kWPl2UYqNfkHR3ohQFUZqX2JQ9X8_S')
        couchIP = decrypted.decode()
        decrypted = f.decrypt(b'gAAAAABezWar8dfCCfQhnRZRNHZ2HdqaSdL4moXv4jkJY8lbxD68_mRV63QrLwmPm-1ctzXivTt80IVJ7KZZQhaBS3Fum8oJ6fy85fPOw_VDUWz9ZotCg95XToXHYwUzYefAdHoQ-HLc')
        STEAM_API_KEY = decrypted.decode()
        print(couchIP)
        print(STEAM_API_KEY)
        start_program(get_last_account_id())
    except BaseException as e:
        print("Invalid Password")

