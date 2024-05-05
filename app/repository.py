from sqlalchemy import create_engine, text
from app import app
from collections import Counter

class Repository:
    
    def __init__(self, DBUSER, DBPASSWORD, HOST, DATABASE):
        try:
            self.engine = create_engine(f'mysql+pymysql://{DBUSER}:{DBPASSWORD}@{HOST}/{DATABASE}')
            self.conn = self.engine.connect()

        except Exception as e:
            app.logger.warning('Could not connect to the database on client.py file.')
            app.logger.warning(f'Verify your credentials for {DBUSER}.')
            app.logger.warning(e)

    def select_all_tracks(self, listed_artists, popular_artists, not_explicit, from_year, to_year):
        query = f'''SELECT t.name, a.name as artist, al.name as album, al.year, t.uri, al.img, acousticness, danceability, energy, instrumentalness, liveness, speechiness, valence, tempo
FROM tracks t
JOIN artists_tracks at ON t.id = at.track_id
JOIN artists a ON a.id = at.artist_id
JOIN albums al ON al.id = t.album_id
WHERE al.year >= {from_year} AND al.year <= {to_year}'''
        if listed_artists != 0:
            comma = "','"
            query += f" AND at.artist_id NOT IN ('{comma.join(listed_artists)}') "
        if popular_artists:
            query += "AND a.popularity <= 30 "
        if not_explicit:
            query += "AND t.explicit = false"
        query = query.replace('\n', ' ')
        print(query)
        return self.conn.execute(text(f"{query}"))

    def select_counts(self):
        tracks_count = self.conn.execute("select count(1) as tracks from tracks;").fetchone()['tracks']
        artists_count = self.conn.execute("select count(1) as artists from artists;").fetchone()['artists']
        albums_count = self.conn.execute("select count(1) as albums from albums;").fetchone()['albums']
        years = self.conn.execute("select (max(year) - min(year)) as years from albums;").fetchone()['years']
        return {"tracks": tracks_count, "artists": artists_count, "albums": albums_count, "years": years}

    def select_albums_by_year(self):
        result = self.conn.execute("select year, count(1) as albums from albums group by year order by 1 asc;")
        albums_list = []
        for row in result:
            albums_list.append({"year": row["year"], "albums": row["albums"]})
        return albums_list

    def select_artists_by_popularity(self):
        result = self.conn.execute("select popularity, count(1) as artists from artists where popularity != 0 group by popularity order by 1 asc")
        return [{"popularity": x["popularity"], "artists": x["artists"]} for x in result]
    

    def select_artists_by_genres(self):
        query = ("""
            SELECT id, name, genres
            FROM artists
            WHERE genres NOT IN ('','0')
        """)
        result = self.conn.execute(query)
        artists = [dict(row) for row in result]

        genre_counts = Counter()
        for artist in artists:
            genres = artist['genres'].split(',')
            genre_counts.update(genres)

        top_genres = genre_counts.most_common(20)
        return [{"genre": genre, "artists": count} for genre, count in top_genres]
    
    def select_all_artists(self):
        result = self.conn.execute("select id, name from artists where name != '0' order by name;")
        return [{"id": x["id"], "name": x["name"]} for x in result]
    
    def select_artist_features(self, artist_id):
        result = self.conn.execute(f'''
        select a.name, AVG(acousticness) as acousticness, AVG(danceability) as danceability, AVG(energy) as energy, AVG(instrumentalness) as instrumentalness,
        AVG(liveness) as liveness, AVG(speechiness) speechiness, AVG(valence) as valence
        from tracks t
        join artists_tracks at on t.id = at.track_id
        join artist a on a.id = at.artist_id
        where a.id = '{artist_id}'
        group by a.name
        ''')
        artist = result.fetchone()
        return artist['name'], [artist['acousticness'], artist['danceability'], artist['energy'],
        artist['instrumentalness'], artist['liveness'], artist['speechiness'], artist['valence']]
    
    def select_top_artists(self, top):
        result = self.conn.execute(f'''
        select a.name, a.popularity, a.img, a.genres
        from artists a
        order by a.popularity desc
        limit {top};
        ''')
        return [{"popularity": x["popularity"], "name": x["name"], "img": x["img"], "genres": x["genres"]} for x in result]
