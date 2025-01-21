import time
import sys
import traceback
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
import config
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException
from sqlalchemy import create_engine
from time import sleep
from sqlalchemy import text

phase = 1

def connectToAPI():
    while True:
        try:
            print("Trying to connect to Spotify API")
            start_time = time.time()
            sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials
                                (client_id=config.SPOTIFY_CLIENT_ID, 
                                client_secret=config.SPOTIFY_CLIENT_SECRET),
                                requests_timeout=1,retries=1)
            end_time = time.time()
            print("Connection established. Time taken:", end_time - start_time, "seconds")
            return sp
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 429:
                retry_after = int(err.response.headers['Retry-After'])
                print(f"You've been rate limited by Spotify. Retrying in {retry_after} seconds...")
                time.sleep(retry_after)
            else:
                print("HTTP error occurred:", err)
                break
        except Exception as e:
            print(e)
            print("Failed to establish connection:", e)
            print("Retrying in 2 minutes...")
            time.sleep(120)

def getStatus(phase):
    trans = conn.begin()
    res = conn.execute(text(f"SELECT status FROM progress WHERE phase = {phase}")).fetchall()[0][0]
    trans.commit()
    return res

def setStatusAsDone(phase):
    trans = conn.begin()
    conn.execute(text(f"UPDATE progress SET status = 1 WHERE phase = {phase} "))
    trans.commit()


try:
    print("Starting db connection")
    db_path = f'mysql+pymysql://{config.DBUSER}:{config.DBPASSWORD}@{config.HOST}/{config.DATABASE}'
    engine = create_engine(db_path)
    conn = engine.connect()
    print("### Connection to database established")
except Exception as e:
    print(e)
    print("could not establish connection to db, shutting down...")
    exit()

sp = connectToAPI()
initial_artists = [
    'the beatles',
    'the rolling stones',
    'the doors',
    'led zeppelin',
    'creedence clearwater revival',
    'barbara strisand',
    'pink floyd',
    'eagles',
    'queen',
    'abba',
    'david bowie',
    'ac dc',
    'black sabbath',
    'aerosmith',
    'michael jackson',
    'phil collins',
    'u2',
    'bon jovi',
    'metallica',
    'journey',
    'guns n roses',
    'whitney houston',
    'bryan adams',
    'elton john',
    'celine dion',
    'mariah carey',
    'nirvana',
    'madonna',
    'red hot chili peppers',
    'oasis',
    'the smiths',
    'the verve',
    'spice girls',
    'green day',
    'cranberries',
    'eminem',
    'linkin park',
    'coldplay',
    'britney spears',
    'beyonce',
    'robbie williams',
    'nickelback',
    'black eyed peas',
    'avril lavigne',
    'rihanna',
    'lady gaga',
    'shakira',
    'adele',
    'ed sheeran',
    'justin bieber',
    'taylor swift',
    'bruno mars',
    'drake',
    'bts',
    'maroon 5',
    'katy perry',
    'ariana grande',
    'the weeknd',
    'imagine dragons',
    'boris brejcha',
    'worakls',
    'avicii',
    'martin garrix',
    'calvin harris',
    'solomun',
    'enrico sangiuliano',
    'charlotte de witte',
    'monika kruse',
    'adam beyer',
    'mind against',
    'maceo plex',
    'alok',
    'sam paganini',
    'anna',
    'carl cox',
    'kolsch',
    'la vela puerca',
    'el cuarteto de nos',
    'cuatro pesos de propina',
    'callejeros',
    'las pastillas del abuelo',
    'los autenticos decadentes',
    'los rodriguez',
    'andres calamaro',
    'legiao urbana',
    'tribalistas',
    'gilberto gil',
    'caetano veloso',
    'cazuza',
    'thiaguinho',
    'mc kevinho',
    'anitta',
    'capital inicial',
    'of monsters and men',
    'kodaline',
    'twenty one pilots',
    'stereophonics',
    'the 1975',
    'm83',
    'two door cinema club',
    'billie eilish',
    'jimi hendrix'
]

print("things are initialized")
print(f"PHASE {phase}: ",getStatus(phase))
if getStatus(phase) == 0:
    trans = conn.begin()
    print("Searches for each artist in the initial_artists list on the Spotify API, and inserts their data into the artists table.")
    for index, artist in enumerate(initial_artists, start=1):
        try:
            data = sp.search(artist, limit=1, type='artist')['artists']['items'][0]
            id = data['id']
            name = data['name'].replace("'", "")
            genres = ','.join(data['genres']).replace("'", "")
            popularity = data['popularity']
            try:
                img = data['images'][0]['url']
            except:
                img = ''
            uri = data['uri']
            conn.execute(text(f"INSERT IGNORE INTO artists (id,name,genres,popularity,img,uri,tracks_dumped,processed) VALUES ('{id}','{name}','{genres}','{popularity}','{img}','{uri}',false,false)"))
            print(f"{index}/{len(initial_artists)}: {name}")
            sleep(1.5)
        except Exception as e:
            print(f"Error occurred for artist {artist}: {e}")
            continue

    trans.commit()
    setStatusAsDone(phase)
    phase += 1
else:
    phase +=1

print(f"PHASE {phase}: ",getStatus(phase))
if getStatus(phase) == 0:
    trans = conn.begin()
    print("Fetches the artists related to each artist in  database from the Spotify API, and inserts their data into the artists table.")
    result = conn.execute(text(f"SELECT id FROM artists"))
    for index,row in enumerate(result, start=1):
        print(index)
        try:
            artists = sp.artist_related_artists(row[0])['artists']
            sleep(1.5)
            for artist in artists:
                id = artist['id']
                name = artist['name'].replace("'","")
                genres = ','.join(artist['genres']).replace("'","")
                popularity = artist['popularity']
                try:
                    img = artist['images'][0]['url']
                except:
                    img = ''
                uri = artist['uri']
                conn.execute(text(f"INSERT IGNORE INTO artists (id,name,genres,popularity,img,uri,tracks_dumped,processed) VALUES ('{id}','{name}','{genres}','{popularity}','{img}','{uri}',false,false)"))
                print(f'{index}/{result.rowcount}')
        except Exception as e:
            print(f"Error occurred: {e}")
            continue

    trans.commit()
    setStatusAsDone(phase)
    phase += 1
else:
    phase +=1

print(f"PHASE {phase}: ",getStatus(phase))
if getStatus(phase) == 0:
    counter = 0
    trans = conn.begin()
    albumSleepTimer = 1.5
    print("Fetches the albums and singles for each artist in your database from the Spotify API, inserts their data into the albums table, and updates the artists and artists_albums tables as necessary.")
    result = conn.execute(text("SELECT id FROM artists WHERE tracks_dumped = false AND name != '0'"))
    total_rows = result.rowcount
    for index,row in enumerate(result, start=1):
        start_time = time.time()
        try:
            sleep(albumSleepTimer)
            print("----")
            albums = sp.artist_albums(row[0],album_type='album,single')['items']
            counter += 1
            albumCount = len(albums)
            print("### ARTIST PROCESSING ESTIMATED TIME: ", (albumCount * albumSleepTimer) / 60, "minutes")
            for counter, x in enumerate(albums, start=1):
                album = sp.album(x['id']) 
                counter += 1
                sleep(albumSleepTimer)
                album_name = album['name'].replace("'","")
                try:
                    img = album['images'][0]['url']
                except:
                    img = ''
                print(f"{x['artists'][0]['name']} --  {counter}/{albumCount} -- {index}/{result.rowcount} -- {album_name}")
                if conn.execute(text(f"SELECT id FROM albums WHERE id = '{album['id']}'")).rowcount == 0:
                    conn.execute(text(f"INSERT IGNORE INTO albums (id,name,type,popularity,year,img,uri) VALUES ('{album['id']}','{album_name}','{album['album_type']}','{album['popularity']}','{album['release_date'][:4]}','{img}','{album['uri']}')"))
                for artist in album['artists']:
                    if conn.execute(text(f"select id from artists where id = '{artist['id']}'")).rowcount == 0:
                        conn.execute(text(f"INSERT IGNORE INTO artists (id,name,genres,popularity,img,uri,tracks_dumped,processed) values ('{artist['id']}','0','0','0','0','0',false,false) "))
                    conn.execute(text(f"INSERT IGNORE INTO artists_albums (artist_id,album_id) values ('{artist['id']}','{album['id']}') "))
                pass
            conn.execute(text(f"update artists set tracks_dumped='1' where id='{row[0]}'"))

            elapsed_time = time.time() - start_time
            remaining_rows = total_rows - index
            estimated_time_remaining = elapsed_time * remaining_rows
            hours, remainder = divmod(estimated_time_remaining, 3600)
            minutes, _ = divmod(remainder, 60)

            print(f"## Estimated time remaining: {int(hours)} hours and {int(minutes)} minutes")
            
        except Exception as e:
            print(f"Error occurred: {e}")
            continue
    trans.commit()
    setStatusAsDone(phase)
    phase += 1
else:
    phase +=1
#
print(f"PHASE {phase}: ",getStatus(phase))
if getStatus(phase) == 0:
    trans = conn.begin()
    print("Fetches the details for each artist in your database with placeholder values from the Spotify API, and updates their data in the artists table.")
    result = conn.execute(text(f"SELECT id FROM artists WHERE name = '0' AND genres = '0'"))
    for index,row in enumerate(result, start=1):
        try:
            artist = sp.artist(row[0])
            sleep(1.5)
            id = artist['id']
            name = artist['name'].replace("'","")
            genres = ','.join(artist['genres']).replace("'","")
            popularity = artist['popularity']
            try:
                img = artist['images'][0]['url']
            except:
                img = ''
            uri = artist['uri']
            conn.execute(text(f"update artists set name='{name}',genres='{genres}',popularity='{popularity}',img='{img}',uri='{uri}',tracks_dumped=false,processed=false where id='{id}'"))
            print(f'{index}/{result.rowcount} {name}')
        except Exception as e:
            print(f"Error occurred: {e}")
            continue
    trans.commit()
    setStatusAsDone(phase)
    phase += 1
else:
    phase +=1

print(f"PHASE {phase}: ",getStatus(phase))
if getStatus(phase) == 0:
    trans = conn.begin()
    print("Fetches the tracks for each album in your database from the Spotify API, inserts their data into the tracks table, and updates the albums, artists, and artists_tracks tables as necessary.")
    result = conn.execute(text(f"select id, name from albums where tracks_dumped = '0'"))
    for i, row in enumerate(result, start=1):
        try:
            tracks_in_album = sp.album_tracks(row[0])['items']
            # print(tracks_in_album)
            sleep(1.5)
            features = sp.audio_features([x['id'] for x in tracks_in_album])
            sleep(1.5)
            # print(features)
            features = [x if x != None else {'acousticness': 0, 'danceability': 0, 'duration_ms': 0, 'energy': 0, 'instrumentalness': 0, 'key': 0, 'liveness': 0, 'valence':0, 'loudness': 0, 'mode': 0, 'speechiness': 0, 'tempo': 0, 'time_signature': 0} for x in features]
            for index, track in enumerate(tracks_in_album,start=0):
                conn.execute(text(f"""
                INSERT IGNORE INTO tracks (`id`, `name`, `explicit`, `uri`, `duration`, `key`, `mode`, `time_signature`, `acousticness`, `danceability`, `energy`, `instrumentalness`, `liveness`, `loudness`, `speechiness`, `valence`, `tempo`, `album_id`)
                values('{track['id']}','{track['name'].replace("'","").replace("-","").replace("%","")}','{track['explicit']}','{track['uri']}','{track['duration_ms']}','{features[index]['key']}',
                '{features[index]['mode']}','{features[index]['time_signature']}','{features[index]['acousticness']}','{features[index]['danceability']}',
                '{features[index]['energy']}','{features[index]['instrumentalness']}','{features[index]['liveness']}','{features[index]['loudness']}',
                '{features[index]['speechiness']}','{features[index]['valence']}','{features[index]['tempo']}','{row[0]}') 
                """))
                for artist in track['artists']:
                    if conn.execute(text(f"select id from artists where id ='{artist['id']}'")).rowcount == 0:
                        conn.execute(text(f"INSERT IGNORE INTO artists (id,name,genres,popularity,img,uri,albums_dumped,processed) values ('{artist['id']}','0','0','0','0','0',false,false) "))
                    conn.execute(text(f"INSERT IGNORE INTO artists_tracks (artist_id, track_id) values ('{artist['id']}','{track['id']}') "))
            conn.execute(text(f"update albums set tracks_dumped = '1' where id = '{row[0]}'"))
            print(f"{round((i/result.rowcount)*100,2)}% {row[1]}")
        except SpotifyException as e:
            if e.http_status == 429:
                retry_after = int(e.headers.get('Retry-After', 120))
                print(f"You've been rate limited by Spotify. Retrying in {retry_after} seconds...")
                time.sleep(retry_after)
                print("Too many requests made to the Spotify API, exiting.")
                sys.exit(1)
            else:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback_details = traceback.extract_tb(exc_traceback)
                filename, line_number, func_name, text = traceback_details[-1]

                print(f"An error occurred at line {line_number}: {e}")
                print(traceback.format_exc())
                exit()
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback_details = traceback.extract_tb(exc_traceback)
            filename, line_number, func_name, text = traceback_details[-1]

            print(f"An error occurred at line {line_number}: {e}")
            print(traceback.format_exc())
            exit()
            continue
    conn.execute(text(f"UPDATE artists SET processed = '1' WHERE tracks_dumped = '1'"))
    trans.commit()
    setStatusAsDone(phase)
    phase += 1
else:
    phase +=1

setStatusAsDone(phase)
