import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import sys
from stringcolor import cs
import requests
import couchdb
import time


api_count = 0


def init_couch_db():
    couch = couchdb.Server(couchIP)
    dbread = couch['aussteamids']
    db = couch['steamids']
    db2 = couch['aussteamids']
    return db, db2, dbread


def create_or_get_documents(db, steam_id):
    doc_id = str(steam_id)
    if doc_id in db:
        regular_doc = db[doc_id]
    else:
        db[doc_id] = {}
        regular_doc = db[doc_id]
    return regular_doc


def start_program(account_id=0):
    global api_count
    db, db2, dbread = init_couch_db()
    for d_id in dbread.view('_all_docs'):
        doc_id = d_id['id']
        url2 = f'http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={STEAM_API_KEY}&steamid={doc_id}&relationship=friend'
        api_count += 1
        if api_count >= 100:
                api_count = 0
                print('waiting for a minute...')
                time.sleep(60)
        resp = requests.get(url2)
        friend = resp.json()
        if 'friendslist' in friend and 'friends' in friend['friendslist']:
            listfriends = friend['friendslist']['friends']
            for x in listfriends:
                steam_id = x['steamid']
                get_player_data(steam_id, db, db2)
            


def get_player_data(steam_id, db, db2):
    global api_count
    print(cs(f'Fetching player data for steamid {steam_id}', '#b4d3fa'))
    url = f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={STEAM_API_KEY}&steamids={steam_id}'
    resp = requests.get(url)
    api_count += 1
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


def save_to_db(db, steam_id, info, db2):
    aus_doc = create_or_get_documents(db, steam_id)
    for key in info:
        try:
            aus_doc[key] = info[key]
            db.save(aus_doc)
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
        decrypted = f.decrypt(b'gAAAAABezWarPJtSItCKAVLGxcezAA6Enb-eQXaTFixcGaD0Sdqanb1pjHDgyp0BhkSgqC0n6S8AfTXYJKgAPR6hqegTYpOVqn4Y6X9Rxt6HCqVkj2qX-ywc3rKQ8kxjkkvYhHhlt1pc')
        STEAM_API_KEY = decrypted.decode()
        start_program()
    except BaseException as e:
        print("Invalid Password")
