from threading import Thread
import tkinter as tk
from urllib.request import urlopen
from typing import Any

from PIL import ImageTk, Image

import utils


class Sizing:
    SPACE_UNIT = 10
    PLAY_BUTTON_SIZE = 64
    SIDE_BUTTON_SIZE = 34
    PROGRESS_BAR_HEIGHT = 15
    TIMESTAMP_LABEL_HEIGHT = 15


class CleanWindow(tk.Tk):
    def __init__(self, display_in_window=False):
        tk.Tk.__init__(self)

        if display_in_window:
            self.resizable(False, False)
        else:
            self.overrideredirect(True)

        self.configure(bg="black")


class CleanButton(tk.Button):
    def __init__(self, master, **kwargs):
        tk.Button.__init__(self, master, **kwargs)
        self.configure(bg="black", borderwidth=0, highlightthickness=0, activebackground="black",
                       activeforeground="white")


class CleanLabel(tk.Label):
    def __init__(self, master, **kwargs):
        tk.Label.__init__(self, master, bg=master["bg"], fg="white", **kwargs)


class CleanProgressBar(tk.Canvas):
    bar: int

    def __init__(self, master, **kwargs):
        tk.Canvas.__init__(self, master, highlightthickness=0, bg="#4d4d4d", **kwargs)
        self.bar = self.create_rectangle(0, 0, 0, 9999, fill="#1db954", outline="#1db954")

    def set_progress_percentage(self, percentage: float):
        self.itemconfig(self.bar, width=int(percentage * self.winfo_width() * 2))

    def toggle_visibility(self, visible: bool):
        self.configure(bg="#4d4d4d" if visible else "black")

        if not visible:
            self.set_progress_percentage(0)


class FadedText(tk.Canvas):
    text: int

    def __init__(self, master: "SpotifyRemoteWindow", width, font=("Verdana", 11), fill="white", **kwargs):
        tk.Canvas.__init__(self, master, bg=master["bg"], highlightthickness=0, width=width, **kwargs)
        self.text = self.create_text(0, 0, anchor=tk.NW, fill=fill, font=font)
        self.create_image(width - 40, 0, anchor=tk.W, image=master.assets["fade"])

    def update_text(self, new_text: str):
        self.itemconfigure(self.text, text=new_text)


def get_cover_image_for_window(window: "SpotifyRemoteWindow", url: str, size: int):
    try:
        img = Image.open(urlopen(url)).resize((size, size), Image.BICUBIC)
        window.cover_image_stream = ImageTk.PhotoImage(img)
        window.event_generate(window.current_cover_image_sequence)
    except Exception as e:
        print(f"ERROR WHEN LOADING COVER IMAGE:\n{e}\n--------------------")


class SpotifyRemoteWindow(CleanWindow):
    assets: dict[str, tk.PhotoImage]

    play_btn: CleanButton
    prev_btn: CleanButton
    next_btn: CleanButton

    timestamp_current: tk.Label
    timestamp_duration: tk.Label
    progress_bar: CleanProgressBar

    device_icon: tk.Label
    device_label: FadedText

    cover_image: tk.Label
    cover_image_stream: Any | None
    cover_image_size: int
    current_cover_image_sequence: str | None
    current_cover_image_url: str | None
    song_title: FadedText
    song_artist: FadedText

    def __init__(self, *, size: (int, int), display_in_window: bool):
        CleanWindow.__init__(self, display_in_window=display_in_window)
        width, height = size

        # Quick asset loader
        def a(f): return tk.PhotoImage(file=f"assets/{f}")

        self.assets = {
            "pause_icon": a("pause.png"),
            "play_icon": a("play.png"),
            "prev_icon": a("prev.png"),
            "next_icon": a("next.png"),
            "fade": a("fade.png"),
            "device_none": a("devices/none.png"),
            "device_default": a("devices/default.png"),
        }

        self.title("Spotify Remote UI")
        self.geometry("%dx%d" % size)

        # Playback controls
        self.play_btn = CleanButton(self, image=self.assets["play_icon"])
        self.prev_btn = CleanButton(self, image=self.assets["prev_icon"])
        self.next_btn = CleanButton(self, image=self.assets["next_icon"])

        self.place_playback_controls()
        self.set_playing_status(False)

        # Timestamps and progress bar
        self.timestamp_current = CleanLabel(self, text="0:00", anchor=tk.W, font=("Verdana", 14))
        self.timestamp_current.place(
            x=Sizing.SPACE_UNIT,
            y=self.play_btn.winfo_y() - Sizing.TIMESTAMP_LABEL_HEIGHT,
            width=width // 2 - Sizing.SPACE_UNIT,
            height=Sizing.TIMESTAMP_LABEL_HEIGHT
        )
        self.update()

        self.timestamp_duration = CleanLabel(self, text="0:00", anchor=tk.E, font=("Verdana", 14))
        self.timestamp_duration.place(
            x=width // 2,
            y=self.timestamp_current.winfo_y(),
            width=width // 2 - Sizing.SPACE_UNIT,
            height=Sizing.TIMESTAMP_LABEL_HEIGHT
        )
        self.update()

        self.progress_bar = CleanProgressBar(self)
        self.progress_bar.place(
            x=Sizing.SPACE_UNIT,
            y=self.timestamp_current.winfo_y() - Sizing.PROGRESS_BAR_HEIGHT - Sizing.SPACE_UNIT // 2,
            width=width - Sizing.SPACE_UNIT * 2,
            height=Sizing.PROGRESS_BAR_HEIGHT
        )
        self.update()

        # Device label
        self.device_icon = CleanLabel(self, image=self.assets["device_none"])
        self.device_icon.place(x=Sizing.SPACE_UNIT, y=Sizing.SPACE_UNIT // 2)
        self.update()

        self.device_label = FadedText(
            self,
            font=("Verdana", 17),
            fill="#d4d4d4",
            width=width - self.device_icon.winfo_x() - self.device_icon.winfo_width() - Sizing.SPACE_UNIT
        )
        self.device_label.place(
            x=self.device_icon.winfo_x() + self.device_icon.winfo_width() + Sizing.SPACE_UNIT,
            y=self.device_icon.winfo_y() + 1,
            height=self.device_icon.winfo_height()
        )
        self.update()

        # Cover image and song info
        self.current_cover_image_sequence = None
        self.current_cover_image_url = None

        self.cover_image = CleanLabel(self)
        cover_image_y = self.device_icon.winfo_y() + self.device_icon.winfo_height() + Sizing.SPACE_UNIT
        self.cover_image_size = height - cover_image_y - (height - self.progress_bar.winfo_y()) - Sizing.SPACE_UNIT
        self.cover_image.place(
            x=Sizing.SPACE_UNIT,
            y=cover_image_y,
            width=self.cover_image_size,
            height=self.cover_image_size
        )
        self.update()

        self.song_title = FadedText(
            self,
            font=("Verdana", 28, "bold"),
            width=width - self.cover_image.winfo_x() - self.cover_image.winfo_width() - Sizing.SPACE_UNIT * 2
        )
        self.song_title.place(
            x=self.cover_image.winfo_x() + self.cover_image.winfo_width() + Sizing.SPACE_UNIT,
            y=self.cover_image.winfo_y(),
            height=50
        )
        self.update()

        self.song_artist = FadedText(
            self,
            font=("Verdana", 14),
            width=self.song_title.winfo_width()
        )
        self.song_artist.place(
            x=self.song_title.winfo_x(),
            y=self.song_title.winfo_y() + self.song_title.winfo_height(),
            height=22
        )

        self.song_title.update_text("Waiting for Spotify...")

    def place_playback_controls(self):
        width, height = self.winfo_width(), self.winfo_height()

        self.play_btn.place(
            x=(width - Sizing.PLAY_BUTTON_SIZE) // 2,
            y=height - Sizing.PLAY_BUTTON_SIZE - Sizing.SPACE_UNIT,
            width=Sizing.PLAY_BUTTON_SIZE,
            height=Sizing.PLAY_BUTTON_SIZE
        )
        self.update()

        self.prev_btn.place(
            x=(0.5 * width - Sizing.SIDE_BUTTON_SIZE) // 2,
            y=height - Sizing.SIDE_BUTTON_SIZE - Sizing.SPACE_UNIT - (Sizing.PLAY_BUTTON_SIZE - Sizing.SIDE_BUTTON_SIZE) // 2,
            width=Sizing.SIDE_BUTTON_SIZE,
            height=Sizing.SIDE_BUTTON_SIZE
        )
        self.update()

        self.next_btn.place(
            x=(1.5 * width - Sizing.SIDE_BUTTON_SIZE) // 2,
            y=self.prev_btn.winfo_y(),
            width=Sizing.SIDE_BUTTON_SIZE,
            height=Sizing.SIDE_BUTTON_SIZE
        )
        self.update()

    def on_cover_loaded(self, event):
        self.unbind_all(self.current_cover_image_sequence)
        self.current_cover_image_sequence = None
        self.cover_image.configure(image=self.cover_image_stream)

    def set_playing_status(self, is_playing: bool | None):
        if is_playing is None:
            self.play_btn.place_forget()
            self.next_btn.place_forget()
            self.prev_btn.place_forget()
            return

        self.place_playback_controls()
        self.play_btn.configure(image=self.assets["pause_icon" if is_playing else "play_icon"])

    def set_progress_bar_value(self, percentage: float | None):
        if percentage is None:
            self.progress_bar.toggle_visibility(False)
            return

        self.progress_bar.toggle_visibility(True)
        self.progress_bar.set_progress_percentage(percentage)

    def set_timestamps(self, current: str, duration: str):
        self.timestamp_current.configure(text=current)
        self.timestamp_duration.configure(text=duration)

    def set_device(self, name: str, device_type: str):
        self.device_label.update_text(name)
        self.device_icon.configure(image=self.assets[f"device_{device_type}"])

    def set_cover_image(self, url: str | None):
        if url is None:
            self.unbind_all(self.current_cover_image_sequence)
            self.current_cover_image_sequence = None
            self.current_cover_image_url = None
            self.cover_image.configure(image="")

        if self.current_cover_image_url == url:
            return

        if self.current_cover_image_sequence is not None:
            self.unbind_all(self.current_cover_image_sequence)

        self.current_cover_image_sequence = f"<<Image{utils.unix_millis()}Loaded>>"
        self.bind(self.current_cover_image_sequence, self.on_cover_loaded)
        Thread(target=get_cover_image_for_window, args=(self, url, self.cover_image_size)).start()

    def set_song_info(self, title: str, artist: str):
        self.song_title.update_text(title)
        self.song_artist.update_text(artist)
