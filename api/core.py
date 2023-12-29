import spotipy
from spotipy.oauth2 import SpotifyOAuth

import api.models as models


class SpotifyApi:
    client: spotipy.Spotify

    def __init__(self, *, client_id: str, client_secret: str, redirect_uri: str):
        self.client = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scope="user-read-playback-state user-modify-playback-state"
            )
        )

    @property
    def current_playback(self) -> models.PlaybackState | None:
        data = self.client.current_playback()

        return models.PlaybackState(data) if data is not None else None
