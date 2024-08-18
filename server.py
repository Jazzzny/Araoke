import pygame
import webview
import threading
import os
import time
import api_internal
import search_support

# 693751201

# Initialize pygame mixer
pygame.mixer.init()

araokeapi = api_internal.AraokeAPI()
search = search_support.MusicSearch()

channels = [pygame.mixer.Channel(i) for i in range(4)]

player_state = {
    'enabled': [True, True, True, True],
    'queue': [],
    'tracks': []
}

stop_event = threading.Event()
state_lock = threading.Lock()

def next_song():
    while not stop_event.is_set():
        if not channels[0].get_busy():
            # if the queue is 1 long, play_audio, else next_track
            with state_lock:
                if len(player_state['queue']) == 1:
                    print("Queue is 1 long, playing audio.")
                    play_audio()
                elif len(player_state['queue']) > 1:
                    print("Queue is longer than 1, skipping to next track.")
                    next_track()
        time.sleep(0.5)

def play_audio():
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

def unpause_audio():
    for channel in channels:
        channel.unpause()

def next_track():
    with state_lock:
        stop_audio()
        if player_state['queue']:
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
        song_data = search.id_to_track_info(song_id)

        is_prepared = araokeapi.check_song_prepared(song_id)
        print("Is song prepared:", is_prepared)

        if is_prepared != 1:
            prepare_thread = threading.Thread(target=araokeapi.prepare_song, args=(song_data,))
            prepare_thread.start()

        with state_lock:
            player_state['queue'].append(song_id)
            print("Queue after adding song:", player_state['queue'])



# Create a webview window
api = Api()
window = webview.create_window('Audio Player', 'index.html', js_api=api)

next_song_thread = threading.Thread(target=next_song)
next_song_thread.start()

def on_close():
    print("Closing the window")
    stop_event.set()  # Set the stop event
    print("Stopping the audio")
    stop_audio()
    print("Joining the threads")
    next_song_thread.join()  # Join the thread after setting the stop event
    print("Next song thread joined")

window.events.closed += on_close

webview.start()