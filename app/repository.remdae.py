import time
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from collections import Counter
from time import sleep

class Repository:

    def __init__(self, client_id, client_secret):
        try:
            client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
            self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        except Exception as e:
            print('Could not connect to the Spotify API.')
            print(e)

    def select_all_tracks(self, listed_artists, popular_artists, not_explicit, from_year, to_year):
        tracks = []
        for year in range(from_year, to_year + 1):
            print("Prcessing the ", year,"'s")
            offset = 0
            while True:
                if offset > 950:
                    break
                albums = self.sp.search(q=f'year:{year}', type='album', limit=50, offset=offset)
                print("Album found -> ")
                if not albums['albums']['items']:
                    break
                for album in albums['albums']['items']:
                    album_tracks = self.sp.album_tracks(album['id'])
                    for track in album_tracks['items']:
                        if all(artist['name'] not in listed_artists for artist in track['artists']):
                            if not popular_artists or track['popularity'] <= 30:
                                if not not_explicit or not track['explicit']:
                                    print("Adding: ", track)
                                    tracks.append(track)
                offset += 50
                time.sleep(0.1)

        return tracks

    def select_counts(self):
        tracks_count = self.sp.search(q='track', type='track')['tracks']['total']
        artists_count = self.sp.search(q='artist', type='artist')['artists']['total']
        albums_count = self.sp.search(q='album', type='album')['albums']['total']
        years = self.sp.search(q='album', type='album')['albums']['items'][0]['release_date']
        return {"tracks": tracks_count, "artists": artists_count, "albums": albums_count, "years": years}

    def select_albums_by_year(self):
        results = self.sp.search(q='album', type='album')
        albums_list = []
        for album in results['albums']['items']:
            albums_list.append({"year": album["release_date"], "albums": album["name"]})
        return albums_list

    def select_artists_by_popularity(self):
        results = self.sp.search(q='artist', type='artist')
        return [{"popularity": artist["popularity"], "artists": artist["name"]} for artist in results['artists']['items']]
    

    def select_artists_by_genres(self):
        results = self.sp.search(q='artist', type='artist')
        artists = [artist for artist in results['artists']['items']]

        genre_counts = Counter()
        for artist in artists:
            genres = artist['genres']
            genre_counts.update(genres)

        top_genres = genre_counts.most_common(20)
        return [{"genre": genre, "artists": count} for genre, count in top_genres]
    
    def select_all_artists(self):
        results = self.sp.search(q='artist', type='artist')
        return [{"id": artist["id"], "name": artist["name"]} for artist in results['artists']['items']]
    
    def select_artist_features(self, artist_id):
        result = self.sp.artist_top_tracks(artist_id)
        artist = result['tracks'][0]['artists'][0]
        return artist['name'], [artist['acousticness'], artist['danceability'], artist['energy'],
        artist['instrumentalness'], artist['liveness'], artist['speechiness'], artist['valence']]
    
    def select_top_artists(self, top):
        results = self.sp.search(q='artist', type='artist')
        return [{"popularity": artist["popularity"], "name": artist["name"], "img": artist["images"][0]["url"], "genres": artist["genres"]} for artist in results['artists']['items'][:top]]
