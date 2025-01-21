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
        tracks_count = self.conn.execute(text(f"select count(1) as tracks from tracks;")).fetchone()[0]
        artists_count = self.conn.execute(text(f"select count(1) as artists from artists;")).fetchone()[0]
        albums_count = self.conn.execute(text(f"select count(1) as albums from albums;")).fetchone()[0]
        years = self.conn.execute(text(f"select (max(year) - min(year)) as years from albums;")).fetchone()[0]
        return {"tracks": tracks_count, "artists": artists_count, "albums": albums_count, "years": years}

    def select_albums_by_year(self):
        result = self.conn.execute(text(f"select year, count(1) as albums from albums group by year order by 1 asc;"))
        rows = result.fetchall()
        keys = result.keys()
        albums_list = [dict(zip(keys, row)) for row in rows]
        return albums_list

    def select_artists_by_popularity(self):
        result = self.conn.execute(text(f"select popularity, count(1) as artists from artists where popularity != 0 group by popularity order by 1 asc"))
        rows = result.fetchall()
        keys = result.keys()
        popularity_list = [dict(zip(keys, row)) for row in rows]
        return popularity_list

    def select_artists_by_genres(self):
        query = text("""
            SELECT id, name, genres
            FROM artists
            WHERE genres NOT IN ('','0')
        """)
        result = self.conn.execute(query)
        rows = result.fetchall()
        keys = result.keys()
        artists_list = [dict(zip(keys, row)) for row in rows]
        return artists_list
    
    def select_all_artists(self):
        result = self.conn.execute(text(f"select id, name from artists where name != '0' order by name;"))
        rows = result.fetchall()
        keys = result.keys()
        artists_list = [dict(zip(keys, row)) for row in rows]
        return artists_list
    
    def select_artist_features(self, artist_id):
        result = self.conn.execute(text(f'''
        select a.name, AVG(acousticness) as acousticness, AVG(danceability) as danceability, AVG(energy) as energy, AVG(instrumentalness) as instrumentalness,
        AVG(liveness) as liveness, AVG(speechiness) speechiness, AVG(valence) as valence
        from tracks t
        join artists_tracks at on t.id = at.track_id
        join artists a on a.id = at.artist_id
        where a.id = '{artist_id}'
        group by a.name
        '''))
        row = result.fetchone()
        keys = result.keys()
        artist = dict(zip(keys, row))
        return artist['name'], [artist['acousticness'], artist['danceability'], artist['energy'],
        artist['instrumentalness'], artist['liveness'], artist['speechiness'], artist['valence']]
        
    def select_top_artists(self, top):
        result = self.conn.execute(text(f'''
        select a.name, a.popularity, a.img, a.genres
        from artists a
        order by a.popularity desc
        limit {top};
        '''))
        rows = result.fetchall()
        keys = result.keys()
        return [dict(zip(keys, row)) for row in rows]