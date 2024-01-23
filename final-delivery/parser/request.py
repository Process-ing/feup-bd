import requests
import json
from sys import argv
import os

token = '[INSERT TOKEN HERE]'
headers = {
    'Authorization': f'Bearer {token}',
    'Client-Id': '[INSERT CLIENT ID HERE]',
}

def create_dirs():
    if not os.path.exists("population_files"):
        os.makedirs("population_files")
    if not os.path.exists("population_files/json"):
        os.makedirs("population_files/json")

def get_streams():
    path = "population_files/json/streams.json"
    url1 = 'https://api.twitch.tv/helix/streams?first=100'
    url2 = 'https://api.twitch.tv/helix/streams?first=100&after='
    
    info = requests.get(url1, headers=headers).json()
    data = info['data']
    for i in range(3):
        info = requests.get(url2 + info['pagination']['cursor'], headers=headers).json()
        data += info['data']
    
    
    data = list(
        filter(
            lambda user: user['language'] in ['en', 'fr', 'pt', 'de', 'es'] and not user['is_mature'] and user['title'] != "",
            data
    ))
    print("Streams: ", len(data))
    
    with open(path, 'w') as file:
        file.write(json.dumps(data, indent=4, ensure_ascii=False))
        
def choose_and_request_accounts():
    users_path = 'population_files/json/users.json'
    streamers_path = 'population_files/json/streamers.json'
    old_streams_path = 'population_files/json/streams.json'
    new_streams_path = 'population_files/json/filtered_streams.json'
    
    with open(old_streams_path, 'r') as old_streams_file:
        old_streams = json.load(old_streams_file)
    num_streams = int(input('Select the number of streams to select: '))
    new_streams = []
    j = 0
    for i in range(num_streams):
        while True:
            stream = old_streams[j]
            j += 1
            if input(f"Select stream '{stream['title']}' from '{stream['user_name']}'? ").lower() in ['y', 'yes']:
                new_streams.append(stream)
                break
    
    users = []
    user_count = 0
    base_url = 'https://api.twitch.tv/helix/users'
    user_url = streamer_url = base_url
    for stream in old_streams:
        if stream in new_streams:
            streamer_url += f'{"?" if streamer_url == base_url else "&"}id={stream["user_id"]}'
        else:
            user_url += f'{"?" if user_url == base_url else "&"}id={stream["user_id"]}'
            user_count += 1
            if user_count == 100:
                users.extend(requests.get(user_url, headers=headers).json()['data'])
                user_url = base_url
                user_count = 0
    streamers = requests.get(streamer_url, headers=headers).json()['data']
    if user_url != base_url:
        users.extend(requests.get(user_url, headers=headers).json()['data'])
        
    print("Users:", len(users))
    
    with open(new_streams_path, 'w') as new_streams_file:
        new_streams_file.write(json.dumps(new_streams, indent=4, ensure_ascii=False))
    with open(users_path, 'w') as new_streams_file:
        new_streams_file.write(json.dumps(users, indent=4, ensure_ascii=False))
    with open(streamers_path, 'w') as new_streams_file:
        new_streams_file.write(json.dumps(streamers, indent=4, ensure_ascii=False))
        
def get_chat_rooms():
    url = 'https://api.twitch.tv/helix/chat/settings?broadcaster_id='
    streamers_path = 'population_files/json/streamers.json'
    chat_rooms_path = 'population_files/json/chat_rooms.json'
    chat_rooms = []
    
    with open(streamers_path, 'r') as streamers_file:
        streamers = json.load(streamers_file)
    
    for streamer in streamers:
        chat_rooms.extend(requests.get(url + streamer['id'], headers=headers).json()['data'])
    
    with open(chat_rooms_path, 'w') as chat_rooms_file:
        chat_rooms_file.write(json.dumps(chat_rooms, indent=4, ensure_ascii=False))
    

def main():
    if len(argv) != 2:
        print("Usage: python request.py [ALL | [STREAM | STREAMCATEGORIES | ACCOUNTS | CHATS]...]")
        exit(1)
    if argv[1] == "ALL":
        create_dirs()
        get_streams()
        choose_and_request_accounts()
        get_chat_rooms()
        return
    
    for arg in argv[1:]:
        if arg == "STREAMS":
            create_dirs()
            get_streams()
        elif arg == "ACCOUNTS":
            create_dirs()
            choose_and_request_accounts()
        elif arg == "CHATS":
            create_dirs()
            get_chat_rooms()
        else:
            print("request.py:", arg, "is not a valid argument")
            exit(1)
    
if __name__ == '__main__':
    main()