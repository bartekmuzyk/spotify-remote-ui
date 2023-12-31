import sys
import threading
import time
from datetime import datetime
import locale

import argparse

from ui import SpotifyRemoteWindow, SpotifyRemoteWindowCallbacks
from api.core import SpotifyApi
from api.models import Track as SpotifyTrack, Episode as SpotifyEpisode

parser = argparse.ArgumentParser(
    prog=sys.argv[0],
    description="An application which displays a touch-friendly UI with Spotify playback information and controls"
)
parser.add_argument(
    "client_id",
    type=str,
    help="Spotify app client ID"
)
parser.add_argument(
    "client_secret",
    type=str,
    help="Spotify app client secret"
)
parser.add_argument(
    "--width",
    type=int,
    default=480,
    help="Width of the displayed window in pixels."
)
parser.add_argument(
    "--height",
    type=int,
    default=320,
    help="Height of the displayed window in pixels."
)
parser.add_argument(
    "--windowed",
    action="store_true",
    help="Whether the application should be displayed in a framed or a frameless window."
)
parser.add_argument(
    "-l", "--locale",
    type=str,
    default="en_US.utf8",
    help="The locale. Used by internal functions to display information in the proper language. (e.g. en_US.utf8)"
)
parser.add_argument(
    "--hide-cursor",
    action="store_true",
    help="Whether the cursor should be visible in the window. Most useful for touchscreens."
)
opts = parser.parse_args()

if opts.width < 330:
    print("ERROR: width must be at least 330")
    sys.exit(1)
elif opts.height < 320:
    print("ERROR: height must be at least 320")
    sys.exit(1)

window_size = (opts.width, opts.height)
print("Window size: %dx%d" % window_size)

print(f"Setting locale: {opts.locale}")
locale.setlocale(locale.LC_ALL, opts.locale)

if opts.windowed:
    print("Running in windowed mode")


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


class Callbacks(SpotifyRemoteWindowCallbacks):
    api: SpotifyApi

    def __init__(self, api: SpotifyApi):
        self.api = api

    def pause(self):
        self.api.playback_pause()

    def resume(self):
        self.api.playback_resume()

    def next(self):
        self.api.playback_next_track()

    def previous(self):
        self.api.playback_previous_track()


spotify = SpotifyApi(
    client_id=opts.client_id,
    client_secret=opts.client_secret,
    redirect_uri="http://localhost:7392"
)
window = SpotifyRemoteWindow(
    size=window_size,
    display_in_window=opts.windowed,
    hide_cursor=opts.hide_cursor,
    callbacks=Callbacks(spotify)
)

stop_event = threading.Event()
thread = threading.Thread(target=ui_updater, args=(spotify, window, stop_event), daemon=True)
thread.start()

window.mainloop()
stop_event.set()
thread.join()
