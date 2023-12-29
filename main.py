import os
import sys
import threading
import time
from threading import Thread
from datetime import datetime
import locale

from dotenv import load_dotenv

from api.core import SpotifyApi
from api.models import Track as SpotifyTrack, Episode as SpotifyEpisode
from ui import SpotifyRemoteWindow

load_dotenv()

window_size = (480, 320)

if len(sys.argv) >= 3:
    width, height, *_ = sys.argv[1:]

    if not width.isnumeric():
        print("ERROR: width must be an integer")
        sys.exit(1)
    elif not height.isnumeric():
        print("ERROR: height must be an integer")
        sys.exit(1)

    width, height = int(width), int(height)

    if width < 330:
        print("ERROR: width must be at least 330")
        sys.exit(1)
    elif height < 320:
        print("ERROR: height must be at least 320")
        sys.exit(1)

    print(f"Custom window size: {width}x{height}")
    window_size = (width, height)

print(f"Setting locale: {os.getenv('LOCALE')}")
locale.setlocale(locale.LC_ALL, os.getenv("LOCALE"))


def ui_updater(api: SpotifyApi, target_window: SpotifyRemoteWindow, controller_event: threading.Event):
    while not controller_event.is_set():
        state = None

        try:
            state = api.current_playback
        except Exception as e:
            print(e)

        if state is not None:
            target_window.set_playing_status(state.playing)

            if state.progress is not None:
                target_window.set_progress_bar_value(state.progress.percentage)
                target_window.set_timestamps(state.progress.current_time, state.progress.duration)
            else:
                target_window.set_progress_bar_value(0)
                target_window.set_timestamps("0:00", "")

            target_window.set_device(state.device.name, "default")
            target_window.set_cover_image(state.track.image.url)

            if isinstance(state.track, SpotifyTrack):
                target_window.set_song_info(state.track.name, state.track.artist)
            elif isinstance(state.track, SpotifyEpisode):
                target_window.set_song_info(state.track.name, state.track.show_name)

            time.sleep(0.8)
        else:
            target_window.set_playing_status(None)
            target_window.set_progress_bar_value(None)
            target_window.set_timestamps("", "")
            target_window.set_device(datetime.now().strftime("%H:%M - %d %b %Y"), "none")
            target_window.set_cover_image(None)
            target_window.set_song_info("", "")
            time.sleep(3)

    print("UI Updater shutting down!")


spotify = SpotifyApi(redirect_uri="http://localhost:7392")
window = SpotifyRemoteWindow(size=window_size, display_in_window=os.getenv("INWINDOW") == "1")

stop_event = threading.Event()
thread = Thread(target=ui_updater, args=(spotify, window, stop_event), daemon=True)
thread.start()

window.mainloop()
stop_event.set()
thread.join()
