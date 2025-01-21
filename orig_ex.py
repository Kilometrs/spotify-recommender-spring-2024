    def select_artist_features(self, artist_id):
        result = self.conn.execute(f'''
        select a.name, AVG(acousticness) as acousticness, AVG(danceability) as danceability, AVG(energy) as energy, AVG(instrumentalness) as instrumentalness,
        AVG(liveness) as liveness, AVG(speechiness) speechiness, AVG(valence) as valence
        from track t
        join artist_track at on t.id = at.track_id
        join artist a on a.id = at.artist_id
        where a.id = '{artist_id}'
        group by a.name
        ''')
        artist = result.fetchone()
        return artist['name'], [artist['acousticness'], artist['danceability'], artist['energy'],
        artist['instrumentalness'], artist['liveness'], artist['speechiness'], artist['valence']]
    