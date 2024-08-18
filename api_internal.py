import os
import json
import music_isolation
import lyrics_support
import search_support
import youtube_support
import logging

class AraokeAPI:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

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

    def prepare_song(self, song_id):
        logging.info(f"Preparing song {song_id}")
        # get iTunes metadata
        logging.info("Getting metadata")
        song_data = self.search.id_to_track_info(song_id)

        # write the metadata to a json
        logging.info("Writing metadata")
        with open(f"meta/{song_id}.json", "w") as f:
            f.write(json.dumps(song_data))

        # Find the song on YouTube
        logging.info("Searching YouTube")
        youtube_data = self.youtube_search.search(song_data)[0]

        # Download the audio from YouTube
        logging.info("Downloading audio")
        self.downloader.download(f'youtube.com{youtube_data["url_suffix"]}', song_id)

        # Download lyrics
        logging.info("Downloading lyrics")
        self.lyrics.get_lyrics(song_data)

        # Isolate the audio
        logging.info("Isolating audio")
        self.music.isolate(song_id)

        logging.info("Song prepared")
        return 1

    def get_song(self, song_id):
        result = []

        # read the metadata
        with open(f"meta/{song_id}.json", "r") as f:
            song_data = json.loads(f.read())

        result.append(song_data)

        # add the paths to the separated tracks
        result.append([
            f"separated/{song_id}/bass.mp3",
            f"separated/{song_id}/drums.mp3",
            f"separated/{song_id}/other.mp3",
            f"separated/{song_id}/vocals.mp3"
        ])

api = AraokeAPI()
api.prepare_song("693751201")



