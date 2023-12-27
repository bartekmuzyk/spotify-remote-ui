import sys
import tkinter as tk

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

import ui

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

spotify = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        redirect_uri="http://localhost:7392",
        scope="user-read-playback-state user-modify-playback-state"
    )
)


root = tk.Tk()
root.title("Spotify Remote UI")
root.overrideredirect(True)
root.geometry("%dx%d" % window_size)
root.configure(bg="black")

root.assets = {
    "pause_icon": tk.PhotoImage(file="assets/pause.png"),
    "play_icon": tk.PhotoImage(file="assets/play.png")
}

play_btn = ui.CleanButton(root)
play_btn.place(
    x=window_size[0] // 2 - ui.Sizing.PLAY_BUTTON_SIZE // 2,
    y=window_size[1] - ui.Sizing.PLAY_BUTTON_SIZE - ui.Sizing.SPACE_UNIT,
    width=ui.Sizing.PLAY_BUTTON_SIZE,
    height=ui.Sizing.PLAY_BUTTON_SIZE
)


def set_playing_status(is_playing: bool):
    play_btn.configure(image=root.assets["pause_icon" if is_playing else "play_icon"])


set_playing_status(False)

root.mainloop()

# while True:
#     result = models.PlaybackState(spotify.current_playback())
#     print(result)
#     time.sleep(1)
