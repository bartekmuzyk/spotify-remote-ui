from typing import Literal, Optional
from dataclasses import dataclass

import utils


@dataclass
class Image:
    url: str
    size: (int, int)


@dataclass
class Track:
    name: str
    artist: str
    duration: int
    image: Image


@dataclass
class Episode:
    name: str
    show_name: str
    duration: int
    image: Image


@dataclass
class PlaybackProgress:
    current_time: str
    duration: str
    percentage: float


@dataclass
class PlaybackDevice:
    name: str
    type: Literal["computer", "smartphone", "speaker"]


class PlaybackState:
    device: PlaybackDevice
    track: Optional[Track | Episode]
    playing: bool
    progress: Optional[PlaybackProgress]

    def __init__(self, data):
        self.device = PlaybackDevice(
            name=data["device"]["name"],
            type=data["device"]["type"].lower()
        )
        self.playing = data["is_playing"]
        self.track = None
        self.progress = None

        item = data["item"]
        if item is not None:
            if item["type"] == "track":
                self.track = Track(
                    name=item["name"],
                    artist=", ".join([artist["name"] for artist in item["artists"]]),
                    duration=item["duration_ms"],
                    image=Image(
                        url=item["album"]["images"][0]["url"],
                        size=(item["album"]["images"][0]["width"], item["album"]["images"][0]["height"])
                    )
                )
            elif item["type"] == "episode":
                self.track = Episode(
                    name=item["name"],
                    show_name=item["show"]["name"],
                    duration=item["duration_ms"],
                    image=Image(
                        url=item["images"][0]["url"],
                        size=(item["images"][0]["width"], item["images"][0]["height"])
                    )
                )

        if self.track is not None:
            progress_seconds = data["progress_ms"] // 1000 if data["progress_ms"] is not None else 0
            duration_seconds = self.track.duration // 1000
            self.progress = PlaybackProgress(
                current_time=utils.seconds_to_timestamp(progress_seconds),
                duration=utils.seconds_to_timestamp(duration_seconds),
                percentage=round(progress_seconds / duration_seconds, 2)
            )

    def __repr__(self):
        return f"<PlaybackState \"{self.device.name}\" ({self.device.type}), {self.track=}, {self.playing=}, {self.progress.current_time}/{self.progress.duration} - {int(self.progress.percentage * 100)}%>"
