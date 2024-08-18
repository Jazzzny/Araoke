import requests

class MusicSearch:
    def __init__(self, country='CA', limit=3, explicit='Yes'):
        self.country = country
        self.limit = limit
        self.explicit = explicit

    def search_tracks_itunes(self, term):
        results = requests.get(f"https://itunes.apple.com/search?term={term}&entity=song&country={self.country}&limit={self.limit}&explicit={self.explicit}").json()

        tracks = []

        for result in results['results']:
            track = {
                'track_name': result['trackName'],
                'artist_name': result['artistName'],
                'is_explicit': "True" if result['trackExplicitness'] == 'explicit' else "False",
                'track_genre': result['primaryGenreName'],
                'relase_date': result['releaseDate'],
                'track_length': result['trackTimeMillis'],
                'cover_art': result['artworkUrl100'].replace('100x100bb', '1024x1024bb'),
                'id': result['trackId']
            }

            tracks.append(track)

        return tracks

    def id_to_track_info(self, track_id):
        response = requests.get(f"https://itunes.apple.com/lookup?id={track_id}")
        result = response.json()['results'][0]

        track = {
            'track_name': result['trackName'],
            'artist_name': result['artistName'],
            'is_explicit': "True" if result['trackExplicitness'] == 'explicit' else "False",
            'track_genre': result['primaryGenreName'],
            'relase_date': result['releaseDate'],
            'track_length': result['trackTimeMillis'],
            'cover_art': result['artworkUrl100'].replace('100x100bb', '1024x1024bb'),
            'id': result['trackId']
        }

        return track