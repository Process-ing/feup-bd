import json
import os
from random import randint, shuffle, random, choice
from faker import Faker
from datetime import datetime
from dateutil.relativedelta import relativedelta

fake = Faker(locale='en_US')
now = datetime(2023, 11, 15, 23, 59, 59)

def gen_password():
    return fake.password(randint(12, 20))

def gen_email(account):
    if (randint(0, 9) < 3):
        email = f"{account['login']}@{fake.free_email_domain()}"
    else:
        email = fake.free_email()
    return email.replace('hotmail', 'outlook')

def parse_date(date):
    return datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')

def sqlfy_date(date):
    return date.strftime('%Y-%m-%d %H:%M:%S')

def create_dirs():
    if not os.path.exists("population_files"):
        os.makedirs("population_files")
    if not os.path.exists("population_files/sql"):
        os.makedirs("population_files/sql")

def write_accounts():
    users_path = 'population_files/json/users.json'
    streamers_path = 'population_files/json/streamers.json'
    sql_path = 'population_files/sql/accounts.sql'
    with open(users_path, 'r') as users_file:
        users = json.load(users_file)
    with open(streamers_path, 'r') as streamers_file:
        streamers = json.load(streamers_file)
    
    user_usernames = [user['login'] for user in users]
    accounts = users + [streamer for streamer in streamers if streamer['login'] not in user_usernames]
    with open(sql_path, 'w') as sql_file:
        for account in accounts:
            username = account['login']
            email = gen_email(account)
            password = gen_password()
            created_at = parse_date(account['created_at']).strftime("%d/%m/%Y")
            sql_file.write("INSERT INTO Account VALUES "
                           f"('{username}', '{email}', '{password}', '{created_at}');\n")
            
def write_users():
    users_path = 'population_files/json/users.json'
    sql_path = 'population_files/sql/users.sql'
    with open(users_path, 'r') as users_file:
        users = json.load(users_file)
    
    with open(sql_path, 'w') as sql_file:
        for user in users:
            account = user['login']
            sql_file.write(f"INSERT INTO User(account) VALUES ('{account}');\n")
            
def write_streamers():
    streamers_path = 'population_files/json/streamers.json'
    sql_path = 'population_files/sql/streamers.sql'
    with open(streamers_path, 'r') as streamers_file:
        streamers = json.load(streamers_file)
        
    with open(sql_path, 'w') as sql_file:
        for streamer in streamers:
            account = streamer['login']
            profile_picture = streamer['profile_image_url']
            description = streamer['description'].replace("'", "''")
            sql_file.write("INSERT INTO Streamer(account, profilePicture, description) VALUES "
                           f"('{account}', '{profile_picture}', '{description}');\n")
    
def write_streams():
    streams_path = 'population_files/json/filtered_streams.json'
    sql_path = 'population_files/sql/streams.sql'
    
    with open(streams_path, 'r') as streams_file:
        streams = json.load(streams_file)
        
    with open(sql_path, 'w') as sql_file:
        for id, stream in enumerate(streams, start=1):
            title = stream['title'].replace("'", "''")
            streamer = stream['user_login']
            stream_category = stream['game_name'].replace("'", "''")
            start_time = sqlfy_date(parse_date(stream['started_at']))
            language = stream['language']
            sql_file.write("INSERT INTO Stream VALUES "
                           f"({id}, '{streamer}', '{stream_category}', '{title}', '{start_time}', '{language}', 0);\n")

def write_chat_rooms():
    chat_rooms_path = 'population_files/json/chat_rooms.json'
    streamers_path = 'population_files/json/streamers.json'
    sql_path = 'population_files/sql/chat_rooms.sql'
    
    with open(chat_rooms_path, 'r') as chat_rooms_file:
        chat_rooms = json.load(chat_rooms_file)
    with open(streamers_path, 'r') as streamers_file:
        streamers = json.load(streamers_file)
    
    with open(sql_path, 'w') as sql_file:
        for id, chat_room in enumerate(chat_rooms, start=1):
            streamer_username = next(streamer for streamer in streamers if streamer['id'] == chat_room['broadcaster_id'])['login']
            mode = 'slow' if chat_room['slow_mode'] else 'normal'
            message_cooldown = 'NULL' if chat_room['slow_mode_wait_time'] == None else chat_room['slow_mode_wait_time']
            sql_file.write("INSERT INTO ChatRoom VALUES "
                           f"({id}, '{mode}', {message_cooldown}, '{streamer_username}');\n")
            
def write_follows():
    users_path = 'population_files/json/users.json'
    streamers_path = 'population_files/json/streamers.json'
    sql_path = 'population_files/sql/follows.sql'
    follow_dump_path = 'population_files/json/follow_dump.json'
    follows = {}
    
    with open(users_path, 'r') as users_file:
        users = json.load(users_file)
    with open(streamers_path, 'r') as streamers_file:
        streamers = json.load(streamers_file)
    
    nums_follows = sorted((randint(0, len(users) // 3) for _ in streamers), reverse=True)
    with open(sql_path, 'w') as sql_file:
        for streamer, num_follows in zip(streamers, nums_follows):
            streamer_username = streamer['login']
            follows[streamer_username] = []
            following_users = [user for user in users if user['id'] != streamer['id']]
            shuffle(following_users)
            following_users = following_users[:num_follows]
            for user in following_users:
                user_username = user['login']
                follows[streamer_username].append(user_username)
                sql_file.write("INSERT INTO Follows VALUES "
                               f"('{user_username}', '{streamer_username}');\n")
        sql_file.write("\n")
        for streamer, num_follows in zip(streamers, nums_follows):
            streamer_username = streamer['login']
            sql_file.write(f"UPDATE Streamer SET numFollowers={num_follows} WHERE account='{streamer_username}';\n")
    
    with open(follow_dump_path, 'w') as follow_dump:
        follow_dump.write(json.dumps(follows, indent=4, ensure_ascii=False))

def write_subscriptions():
    users_path = 'population_files/json/users.json'
    streamers_path = 'population_files/json/streamers.json'
    follow_dump_path = 'population_files/json/follow_dump.json'
    sql_path = 'population_files/sql/subscriptions.sql'
    
    with open(users_path, 'r') as users_file:
        users = json.load(users_file)
    with open(streamers_path, 'r') as streamers_file:
        streamers = json.load(streamers_file)
    with open(follow_dump_path, 'r') as follow_dump:
        follows = json.load(follow_dump)
    
    with open(sql_path, 'w') as sql_file:
        for streamer_username, followers in follows.items():
            streamer = next(streamer for streamer in streamers if streamer['login'] == streamer_username)
            for user_username in followers:
                user = next(user for user in users if user['login'] == user_username)
                if random() < 0.1:
                    randval = random()
                    if randval < 0.65:
                        tier = 1
                    elif randval < 0.95:
                        tier = 2
                    else:
                        tier = 3
                    streamer_created_at = parse_date(streamer['created_at'])
                    user_created_at = parse_date(user['created_at'])
                    start: datetime = fake.date_time_between(start_date=max(streamer_created_at, user_created_at), end_date=now)
                    start_now_diff = relativedelta(datetime.now(), start)
                    end = start + (relativedelta(years=start_now_diff.years, months=start_now_diff.months + 1) if random() < 0.5 else relativedelta(years=start_now_diff.years + 1))
                    sql_file.write("INSERT INTO Subscription VALUES "
                                   f"('{user_username}', '{streamer_username}', {tier}, '{sqlfy_date(start)}', '{sqlfy_date(end)}');\n")
                    
def write_views():
    streams_path = 'population_files/json/filtered_streams.json'
    streamers_path = 'population_files/json/streamers.json'
    users_path = 'population_files/json/users.json'
    follow_dump_path = 'population_files/json/follow_dump.json'
    sql_path = 'population_files/sql/views.sql'
    view_dump_path = 'population_files/json/view_dump.json'
    
    with open(streams_path, 'r') as streams_file:
        streams = json.load(streams_file)
    with open(streamers_path, 'r') as streamers_file:
        streamers = json.load(streamers_file)
    with open(users_path, 'r') as users_file:
        users = json.load(users_file)
    with open(follow_dump_path, 'r') as follow_dump:
        follows = json.load(follow_dump)
        
    views = {user['login']: [] for user in users}
    streamer_usernames = [streamer['login'] for streamer in streamers]
    view_count = {id: 0 for id in range(1, len(streams) + 1)}
    for user in users:
        user_username = user['login']
        if user_username in streamer_usernames:
            continue
        for stream_id, stream in enumerate(streams, start=1):
            follows_streamer = user_username in follows[stream['user_login']]
            if ((views[user_username] == [] or random() < 0.05) 
                and ((follows_streamer and random() < 0.3) or (not follows_streamer and random() < 0.05))):
                views[user_username].append(stream_id)
                view_count[stream_id] += 1
    
    categories = {stream['game_name'] for stream in streams}.union({ 'Minecraft', 'Just Chatting', 'Fortnite'})
    category_views = {category: 0 for category in categories}
    
    for id, stream in enumerate(streams, start=1):
        category_views[stream['game_name']] += view_count[id]
        
    sorted_categories = sorted(category_views.items(), key=lambda x: x[1], reverse=True)
        
    with open(sql_path, 'w') as sql_file:
        for user, streams_viewing in views.items():
            for stream in streams_viewing:
                sql_file.write(f"INSERT INTO Views VALUES ('{user}', {stream});\n")
        sql_file.write('\n')
        for stream_id in view_count.keys():
            sql_file.write(f"UPDATE Stream SET numViewers={view_count[stream_id]} WHERE id={stream_id};\n")
        sql_file.write('\n')

        for category, numViews in sorted_categories:
            category_name = category.replace('\'', '\'\'')
            sql_file.write(f"UPDATE StreamCategory SET numViewers={numViews} WHERE name='{category_name}';\n")
        sql_file.write('\n')
        for i, (category, _) in enumerate(sorted_categories, start=1):
            category_name = category.replace('\'', '\'\'')
            sql_file.write(f"UPDATE StreamCategory SET ranking={i} WHERE name='{category_name}';\n")
    
    with open(view_dump_path, 'w') as view_dump:
        view_dump.write(json.dumps(views, indent=4, ensure_ascii=False))
        

def write_stream_categories():
    streams_path = 'population_files/json/filtered_streams.json'
    sql_path = 'population_files/sql/stream_categories.sql'
    
    with open(streams_path, 'r') as streams_file:
        streams = json.load(streams_file)
    
    categories = {stream['game_name'].replace("'", "''") for stream in streams}.union({ 'Minecraft', 'Just Chatting', 'Fortnite'})
    
    with open(sql_path, 'w') as sql_file:
        for category in categories:
            sql_file.write(f"INSERT INTO StreamCategory(name) VALUES ('{category}');\n")
            
def write_tags():
    streams_path = 'population_files/json/filtered_streams.json'
    sql_path = 'population_files/sql/tags.sql'
    
    with open(streams_path, 'r') as streams_file:
        streams = json.load(streams_file)
    tags = {tag for stream in streams for tag in stream['tags']}
    
    with open(sql_path, 'w') as sql_file:
        for tag in tags:
            sql_file.write(f"INSERT INTO Tag VALUES ('{tag}');\n")
    
def write_has_tags():
    streams_path = 'population_files/json/filtered_streams.json'
    sql_path = 'population_files/sql/has_tags.sql'
    
    with open(streams_path, 'r') as streams_file:
        streams = json.load(streams_file)
    
    with open(sql_path, 'w') as sql_file:
        for id, stream in enumerate(streams, start=1):
            for tag in stream['tags']:
                sql_file.write(f"INSERT INTO HasTag(stream, tag) VALUES ({id}, '{tag}');\n")

def write_messages():
    messages_path = 'population_files/json/chat_messages.json'
    streamers_path = 'population_files/json/streamers.json'
    view_dump_path = 'population_files/json/view_dump.json'
    chat_rooms_path = 'population_files/json/chat_rooms.json'
    streams_path = 'population_files/json/filtered_streams.json'
    sql_path = 'population_files/sql/messages.sql'
    
    if not os.path.isfile(messages_path):
        streamer_messages = {}
    else:
        with open(messages_path, 'r') as messages_file:
            streamer_messages = json.load(messages_file)
    with open(streamers_path, 'r') as streamers_file:
        streamers = json.load(streamers_file)
    with open(view_dump_path, 'r') as view_dump:
        views = json.load(view_dump)
    with open(streams_path, 'r') as streams_file:
        streams = json.load(streams_file)
    with open(chat_rooms_path, 'r') as chat_rooms_file:
        chat_rooms = json.load(chat_rooms_file)
    
    with open(sql_path, 'w') as sql_file:
        id = 1
        for streamer_name, messages in streamer_messages.items():
            streamer = next(streamer for streamer in streamers if streamer['login'] == streamer_name)
            chat_room_id = next(id for id, chat_room in enumerate(chat_rooms, start=1) if chat_room['broadcaster_id'] == streamer['id'])
            stream_id, stream = next((i, stream) for i, stream in enumerate(streams, start=1) if stream['user_login'] == streamer_name)
            stream_started_at = parse_date(stream['started_at'])
            users_viewing = [user for user, streams_viewing in views.items() if stream_id in streams_viewing]
            for message in messages:
                user = choice(users_viewing)
                content = message.replace("'", "''")
                timestamp = fake.date_time_between(start_date=stream_started_at, end_date=now)
                sql_file.write("INSERT INTO Message VALUES "
                               f"({id}, '{user}', {chat_room_id}, '{content}', '{sqlfy_date(timestamp)}');\n")
                id += 1
                
def write_emoticons():
    streamer_messages_path = 'population_files/json/chat_messages.json'
    sql_path = 'population_files/sql/emoticons.sql'
    
    if not os.path.isfile(streamer_messages_path):
        streamer_messages = {}
    else:
        with open(streamer_messages_path, 'r') as streamer_messages_file:
            streamer_messages = json.load(streamer_messages_file)
        
    emoticons = {emoticon for messages in streamer_messages.values() for message in messages for i, emoticon in enumerate(message.split(':')) if i % 2 == 1}
        
    with open(sql_path, 'w') as sql_file:
        for emoticon in sorted(emoticons):
            sql_file.write(f"INSERT INTO Emoticon VALUES ('{emoticon}');\n")

def write_contains():
    streamer_messages_path = 'population_files/json/chat_messages.json'
    sql_path = 'population_files/sql/contains.sql'
    
    if not os.path.isfile(streamer_messages_path):
        streamer_messages = {}
    else:
        with open(streamer_messages_path, 'r') as streamer_messages_file:
            streamer_messages = json.load(streamer_messages_file)
        
    with open(sql_path, 'w') as sql_file:
        id = 1
        for messages in streamer_messages.values():
            for message in messages:
                emoticons = {emoticon for i, emoticon in enumerate(message.split(':')) if i % 2 == 1}
                for emoticon in sorted(emoticons):
                    sql_file.write(f"INSERT INTO Contains VALUES ({id}, '{emoticon}');\n")
                id += 1
                
def main():
    create_dirs()
    write_accounts()
    write_users()
    write_streamers()
    write_chat_rooms()
    write_stream_categories()
    write_streams()
    write_follows()
    write_subscriptions()
    write_views()
    write_tags()
    write_has_tags()
    write_emoticons()
    write_messages()
    write_contains()
    
if __name__ == '__main__':
    main()