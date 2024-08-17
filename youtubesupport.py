import yt_dlp
import youtube_search

class DownloadAudio:
    def __init__(self, url):
        self.url = url
        self.ydl_opts = {
            'format': 'm4a/bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
            }],
        }

    def download(self):
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download([self.url])


results = youtube_search.YoutubeSearch('Red Rain · Peter Gabriel "Auto-generated by YouTube."', max_results=5).to_json()

print(results)