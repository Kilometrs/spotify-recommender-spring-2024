from flask.json import jsonify
import pandas as pd
from scipy.spatial.distance import cdist
from sklearn.preprocessing import StandardScaler
from app.repository import Repository
from app import config
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy

repository = Repository(config.DBUSER, config.DBPASSWORD, config.HOST, config.DATABASE)
print("Repo initialized")
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=config.SPOTIFY_CLIENT_ID, client_secret=config.SPOTIFY_CLIENT_SECRET))
print("<DEBUG> Track name:", sp.track('6rqhFgbbKwnb9MLmUQDhG6')['name'])

def search(search_string):
    results = []
    if search_string:
        results = sp.search(q=search_string,type="track")['tracks']['items']
    return jsonify(results)

def get_artist_features( artist_id):
    name, features_values = repository.select_artist_features(artist_id)
    features_keys = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness', 'valence']
    data = {features_keys[i]: features_values[i] for i in range(len(features_keys))}
    return jsonify({"name": name, "chart": data})

def get_artists_top( top):
    return jsonify(repository.select_top_artists(top))

def get_counts():
    return jsonify(repository.select_counts())

def get_dataset_stats():
    albums_per_year=repository.select_albums_by_year()
    artists_per_genre=repository.select_artists_by_genres()
    artists_per_popularity=repository.select_artists_by_popularity()
    artist_list=repository.select_all_artists()
    return albums_per_year, artists_per_genre, artists_per_popularity, artist_list

def get_recommendations(from_year, to_year, listed_artists, popular_artists, exclude_explicit, track_ids):
    print("Track IDs:", track_ids)
    names, artists, albums, years, imgs, uris, matches = get_recommendation(from_year, to_year, listed_artists, popular_artists, exclude_explicit, sp.audio_features(track_ids))
    print("RECOMMENDATIONS HAVE BEEN MADE I REALLY HOPE :))))")
    return jsonify ([{"name": names[i], "artist": artists[i], "album": albums[i], "year": int(years[i]), "img": imgs[i], "uri": "https://open.spotify.com/track/" + uris[i][14:], "match": matches[i]} for i in range(len(names))])


def create_similarity(song, dataframe):
    distance_vector = cdist(XA=song,XB=dataframe,metric='euclidean')
    similarities = 1 / (1 + distance_vector)    
    similarity_index = pd.DataFrame(similarities, columns=dataframe.index)
    return similarity_index

def get_recommendation(from_year, to_year, listed_artists, popular_artists, not_explicit, features_list):
    keys_to_remove = ["duration_ms","key","mode","time_signature","loudness","id","uri","track_href","analysis_url","type"]
    for features in features_list:
        for key in keys_to_remove:
            features.pop(key)
    tracks_list = pd.DataFrame.from_dict(repository.select_all_tracks(listed_artists, popular_artists, not_explicit, from_year, to_year),
    orient="columns")
    print(tracks_list)

    if not tracks_list.empty:
        tracks_list.columns=["name", "artist", "album", "year", "uri", "img", "acousticness", "danceability", "energy", "instrumentalness", "liveness", "speechiness", "valence", "tempo"]
    else:
        print('No tracks found for the given parameters.')
        return [], [], [], [], [], [], []

    tracks_list.columns=["name", "artist", "album", "year", "uri", "img", "acousticness", "danceability", "energy", "instrumentalness", "liveness", "speechiness", "valence", "tempo"]
    scaler = StandardScaler()
    tracks_list[["acousticness", "danceability", "energy", "instrumentalness", "liveness", "speechiness", "valence", "tempo"]] = scaler.fit_transform(tracks_list[["acousticness", "danceability", "energy", "instrumentalness", "liveness", "speechiness", "valence", "tempo"]])
    tracks_list.set_index(["name", "artist", "album", "year", "uri", "img"], inplace=True)

    name_list, artist_list, album_list, year_list, img_list, uri_list, match_list = ([] for i in range(7))

    for features in features_list:
        song = pd.DataFrame(columns=['acousticness','danceability','energy','instrumentalness','liveness','speechiness','valence','tempo'])
        if song.empty:
            song = pd.DataFrame(features, index=[0], columns=["acousticness", "danceability", "energy", "instrumentalness", "liveness", "speechiness", "valence", "tempo"])
        else:
            song = song.append(pd.DataFrame(features, index=[0], columns=["acousticness", "danceability", "energy", "instrumentalness", "liveness", "speechiness", "valence", "tempo"]), ignore_index=True)
        song = scaler.transform(song)

        results = create_similarity(song,tracks_list).T[0].sort_values(ascending=False).reset_index()
        name_list.append(results.loc[results[0]<0.95, 'name'].reset_index(drop=True)[0])
        artist_list.append(results.loc[results[0]<0.95, 'artist'].reset_index(drop=True)[0])
        album_list.append(results.loc[results[0]<0.95, 'album'].reset_index(drop=True)[0])
        year_list.append(results.loc[results[0]<0.95, 'year'].reset_index(drop=True)[0])
        img_list.append(results.loc[results[0]<0.95, 'img'].reset_index(drop=True)[0])
        uri_list.append(results.loc[results[0]<0.95, 'uri'].reset_index(drop=True)[0])
        match_list.append(round(results.loc[results[0]<0.95, 0].reset_index(drop=True)[0]*100))
    return name_list, artist_list, album_list, year_list, img_list, uri_list, match_list