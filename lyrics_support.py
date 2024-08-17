import syncedlyrics
import os

class LyricDownloader:
    def __init__(self):
        if not os.path.exists('lyrics'):
            os.makedirs('lyrics')

    def get_lyrics(self, song_data):
        syncedlyrics.search(search_term=f'{song_data["artist_name"]} - {song_data["track_name"]}', enhanced=True, save_path=f"lyrics/{song_data['id']}.lrc")