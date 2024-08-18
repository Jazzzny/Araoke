import pygame
import webview
import threading
import os
import time
import api_internal
import search_support
import flask
import requests
import sys


# Initialize pygame mixer
pygame.mixer.init()

araokeapi = api_internal.AraokeAPI()
searchapi = search_support.MusicSearch()

channels = [pygame.mixer.Channel(i) for i in range(4)]

player_state = {
    'enabled': [True, True, True, True],
    'queue': [],
    'tracks': []
}

stop_event = threading.Event()
pause_event = threading.Event()
state_lock = threading.Lock()

lyrics = []
current_lyric_index = 0

def load_lyrics(song_id):
    global lyrics
    lyrics = []
    lrc_file_path = os.path.join('lyrics', f'{song_id}.lrc')
    if os.path.exists(lrc_file_path):
        with open(lrc_file_path, 'r', encoding='utf-8') as file:
            for line in file:
                time_part, text_part = line.strip().split(']', 1)
                minutes, seconds = map(float, time_part[1:].split(':'))
                time_in_seconds = minutes * 60 + seconds
                lyrics.append((time_in_seconds, text_part))
    else:
        print(f"Lyrics file not found for song ID: {song_id}")
    lyrics.sort(key=lambda x: x[0])  # Sort lyrics by timestamp
    print(lyrics)

def update_lyrics():
    global current_lyric_index
    while not stop_event.is_set():
        while len(player_state['queue']) == 0:
            if stop_event.is_set():
                return
            time.sleep(0.1)
        if current_lyric_index < len(lyrics):
            if current_lyric_index == 0:
                wait_time = lyrics[current_lyric_index][0] - 0.2
                elapsed_time = 0
                while elapsed_time < wait_time and not stop_event.is_set():
                    if pause_event.is_set():
                        while pause_event.is_set() and not stop_event.is_set():
                            time.sleep(0.1)
                    time.sleep(0.1)
                    elapsed_time += 0.1

            escaped_lyric_current = lyrics[current_lyric_index][1].replace("'", "\\'").replace('"', '\\"') if current_lyric_index < len(lyrics) else ""
            escaped_lyric_next = lyrics[current_lyric_index + 1][1].replace("'", "\\'").replace('"', '\\"') if current_lyric_index + 1 < len(lyrics) else ""
            escaped_lyric_next_next = lyrics[current_lyric_index + 2][1].replace("'", "\\'").replace('"', '\\"') if current_lyric_index + 2 < len(lyrics) else ""
            escaped_lyric_next_next_next = (lyrics[current_lyric_index + 3][1].replace("'", "\\'").replace('"', '\\"')) if current_lyric_index + 3 < len(lyrics) else ""
            window.evaluate_js(f"displayLyrics('{escaped_lyric_current}', '{escaped_lyric_next}', '{escaped_lyric_next_next}', '{escaped_lyric_next_next_next}')")
            if current_lyric_index + 1 < len(lyrics):
                next_lyric_time = lyrics[current_lyric_index + 1][0]
                current_time = lyrics[current_lyric_index][0]
                wait_time = next_lyric_time - current_time - 0.18
                elapsed_time = 0
                while elapsed_time < wait_time and not stop_event.is_set():
                    if pause_event.is_set():
                        while pause_event.is_set() and not stop_event.is_set():
                            time.sleep(0.1)
                    time.sleep(0.1)
                    elapsed_time += 0.1
            current_lyric_index += 1
            print("Lyric index:", current_lyric_index, "Lyric:", lyrics[current_lyric_index][1])

def next_song():
    while not stop_event.is_set():
        if not channels[0].get_busy():
            # if the queue is 1 long, play_audio, else next_track
            next_track()
        time.sleep(0.5)

def play_audio():
    global current_lyric_index
    print("Playing audio")
    print("Queue:", player_state['queue'])
    if not player_state['queue']:
        print("Queue is empty, nothing to play.")
        return

    song_id = player_state['queue'][0]
    track_paths = araokeapi.get_separated_tracks(song_id)

    player_state['tracks'] = [pygame.mixer.Sound(track_paths[i]) for i in range(4)]
    for i in range(4):
        channels[i].play(player_state['tracks'][i])

    load_lyrics(song_id)
    current_lyric_index = 0
    print("Playing song ID:", song_id)

def toggle_track(index):
    with state_lock:
        player_state['enabled'][index] = not player_state['enabled'][index]
        player_state['tracks'][index].set_volume(1 if player_state['enabled'][index] else 0)
        print(f"Track {index} {'enabled' if player_state['enabled'][index] else 'disabled'}")

def stop_audio():
    for channel in channels:
        channel.stop()

def pause_audio():
    for channel in channels:
        channel.pause()
    pause_event.set()


def unpause_audio():
    for channel in channels:
        channel.unpause()
    pause_event.clear()

def next_track():
    with state_lock:
        stop_audio()
        if len(player_state['queue']) > 0:
            if len(player_state['queue']) > 1:
                player_state['queue'].pop(0)
            play_audio()
            print("Queue after skipping to next track:", player_state['queue'])
            window.evaluate_js('updateTrackInfo({})'.format(api.get_current_track()))
        else:
            print("Queue is empty, cannot skip to next track.")

class Api:
    def toggle_track(self, index):
        toggle_track(index)
        return player_state['enabled']

    def stop_audio(self):
        stop_audio()
        return "Audio stopped"

    def pause_audio(self):
        pause_audio()
        return "Audio paused"

    def unpause_audio(self):
        unpause_audio()
        return "Audio unpaused"

    def next_track(self):
        next_track()
        return "Next track"

    def get_current_track(self):
        print("Getting current track")
        print("Queue:", player_state['queue'])
        if len(player_state['queue']) > 0:
            song_data = araokeapi.get_song_data_cached(player_state['queue'][0])
            print("Current track:", song_data)
            return song_data
        else:
            return {}

    def add_track_to_queue(self, song_id):
        song_data = searchapi.id_to_track_info(song_id)

        is_prepared = araokeapi.check_song_prepared(song_id)
        print("Is song prepared:", is_prepared)

        if is_prepared != 1:
            prepare_thread = threading.Thread(target=araokeapi.prepare_song, args=(song_data,))
            prepare_thread.start()
        else:
            with state_lock:
                player_state['queue'].append(song_id)
                print("Queue after adding song:", player_state['queue'])

    def get_queue(self):
        global player_state
        queue = []
        for song_id in player_state['queue'][1:]:
            song_data = araokeapi.get_song_data_cached(song_id)
            queue.append(song_data)
        print("Queue:", queue)
        return queue

# Create a webview window
api = Api()
window = webview.create_window('Araoke', 'index.html', js_api=api)

next_song_thread = threading.Thread(target=next_song)
next_song_thread.start()

lyrics_thread = threading.Thread(target=update_lyrics)
lyrics_thread.start()

# Make QR code
araokeapi.make_qr_code()

###### FLASK SERVER

app = flask.Flask(__name__)

@app.route('/')
def search_page():
    return flask.render_template('search.html')

@app.route('/search', methods=['POST'])
def search():
    results = searchapi.search_tracks_itunes(flask.request.form['term'])
    return flask.render_template('results.html', results=results)

@app.route('/select', methods=['POST'])
def select():
    selected_track = flask.request.json
    api.add_track_to_queue(selected_track['id'])
    return flask.jsonify({'status': 'success', 'selected_track': selected_track})



# RUN IN A SEPARATE THREAD
flask_thread = threading.Thread(target=app.run, kwargs={'port': 80, 'host': '0.0.0.0'})
flask_thread.setDaemon(True)
flask_thread.start()


def on_close():
    global lyrics_thread
    global next_song_thread
    print("Closing the window")
    stop_event.set()  # Set the stop event
    print("Stopping the audio")
    stop_audio()
    print("Joining the threads")
    print("Joining next song thread")
    next_song_thread.join()  # Join the thread after setting the stop event
    print("Joining lyrics thread")
    lyrics_thread.join()  # Join lyrics update thread
    print("Threads joined")

window.events.closed += on_close

webview.start()