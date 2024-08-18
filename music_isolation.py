import demucs.api
import os

class MusicIsolation:
    def __init__(self):
        self.separator = demucs.api.Separator(device="mps")
        if not os.path.exists('separated'):
            os.makedirs('separated')

    def isolate(self, itunes_id):
        if not os.path.exists(f'downloads/{itunes_id}.m4a'):
            raise FileNotFoundError(f"downloads/{itunes_id}.m4a not found")

        _, separated = self.separator.separate_audio_file(f"downloads/{itunes_id}.m4a")

        if not os.path.exists(f'separated/{itunes_id}'):
            os.makedirs(f'separated/{itunes_id}')

        for stem, source in separated.items():
            demucs.api.save_audio(source, f"separated/{itunes_id}/{stem}.mp3", samplerate=self.separator.samplerate)
