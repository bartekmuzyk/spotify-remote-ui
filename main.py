import os
import sys
import threading
import time
from threading import Thread

from dotenv import load_dotenv

from api.core import SpotifyApi
from ui import SpotifyRemoteWindow

load_dotenv()

window_size = (480, 320)

if len(sys.argv) >= 3:
    width, height, *_ = sys.argv[1:]
    print(width, height, _)

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


def ui_updater(api: SpotifyApi, target_window: SpotifyRemoteWindow, controller_event: threading.Event):
    while not controller_event.is_set():
        state = api.current_playback
        print(state)
        target_window.set_playing_status(state.playing)
        target_window.set_progress_bar_value(state.progress.percentage)
        target_window.set_timestamps(state.progress.current_time, state.progress.duration)
        target_window.set_device_label(state.device.name)
        target_window.set_cover_image(state.track.image.url)
        time.sleep(0.8)

    print("UI Updater shutting down!")


spotify = SpotifyApi(redirect_uri="http://localhost:7392")
window = SpotifyRemoteWindow(size=window_size, display_in_window=os.getenv("INWINDOW") == "1")

stop_event = threading.Event()
thread = Thread(target=ui_updater, args=(spotify, window, stop_event), daemon=True)
thread.start()

window.mainloop()
stop_event.set()
thread.join()
