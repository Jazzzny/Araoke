import os
import json
import music_isolation
import lyrics_support
import search_support
import youtube_support

class AraokeAPI:
    def __init__(self):

        self.music = music_isolation.MusicIsolation()
        self.lyrics = lyrics_support.LyricDownloader()
        self.search = search_support.MusicSearch()
        self.youtube_search = youtube_support.SearchYoutube()
        self.downloader = youtube_support.DownloadAudio()

        if not os.path.exists('meta'):
            os.makedirs('meta')

    def check_song_prepared(self, song_id):
        # was the song ever downloaded?
        if not os.path.exists(f"downloads/{song_id}.m4a"):
            return -1
        # do the 4 separated tracks exist?
        if not (os.path.exists(f"separated/{song_id}/bass.mp3") and os.path.exists(f"separated/{song_id}/drums.mp3") and os.path.exists(f"separated/{song_id}/other.mp3") and os.path.exists(f"separated/{song_id}/vocals.mp3")):
            return -2
        # does the lyrics file exist?
        if not os.path.exists(f"lyrics/{song_id}.lrc"):
            return -3
        # yay, we good
        return 1

    def prepare_song(self, song_data):
        song_id = song_data["id"]

        print(f"Preparing song {song_id}")

        # write the metadata to a json
        print("Writing metadata")
        with open(f"meta/{song_id}.json", "w") as f:
            f.write(json.dumps(song_data))

        # Find the song on YouTube
        print("Searching YouTube")
        youtube_data = self.youtube_search.search(song_data)[0]

        # Download the audio from YouTube
        print("Downloading audio")
        self.downloader.download(f'youtube.com{youtube_data["url_suffix"]}', song_id)

        # Download lyrics
        print("Downloading lyrics")
        self.lyrics.get_lyrics(song_data)

        # Isolate the audio
        print("Isolating audio")
        self.music.isolate(song_id)

        print("Song prepared")
        return 1

    def get_song_data_cached(self, song_id):
        # read the metadata
        with open(f"meta/{song_id}.json", "r") as f:
            song_data = json.loads(f.read())

        return song_data

    def get_separated_tracks(self, song_id):
        return [
            f"separated/{song_id}/bass.mp3",
            f"separated/{song_id}/drums.mp3",
            f"separated/{song_id}/other.mp3",
            f"separated/{song_id}/vocals.mp3"
        ]