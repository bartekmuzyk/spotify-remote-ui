import time

from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

import models

load_dotenv()


spotify = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        redirect_uri="http://localhost:7392",
        scope="user-read-playback-state user-modify-playback-state"
    )
)

while True:
    result = models.PlaybackState(spotify.current_playback())
    print(result)
    time.sleep(1)
