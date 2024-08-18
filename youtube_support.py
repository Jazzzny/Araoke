import yt_dlp
import youtube_search
import json

class DownloadAudio:
    def __init__(self):
        self.ydl_opts = {
            'format': 'm4a/bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
            }],
        }

    def download(self, url, itunes_id):
        self.ydl_opts['outtmpl'] = f'downloads/{itunes_id}.%(ext)s'
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download(url)

class SearchYoutube:
    def __init__(self):
        self.max_results = 5

    def search(self, song_data):
        # Get the auto-generated upload of the song - it is just the song without all the other crap in the video
        results_json = youtube_search.YoutubeSearch(f'{song_data["track_name"]} · {song_data["artist_name"]} "Auto-generated by YouTube."', max_results=self.max_results).to_json()
        results = json.loads(results_json)["videos"]

        # Sort durations, return song closest to length provided by iTunes (hopefully its the same song!!!!)
        for result in results:
            result["duration"] = (int(result["duration"].split(':')[0]) * 60 + int(result["duration"].split(':')[1])) * 1000

        results.sort(key=lambda x: abs(x["duration"] - song_data["track_length"]))

        return results