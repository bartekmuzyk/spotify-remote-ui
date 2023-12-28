from threading import Thread
import tkinter as tk
from urllib.request import urlopen
from typing import Any

from PIL import ImageTk, Image


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


class CleanProgressBar(tk.Canvas):
    bar: int

    def __init__(self, master, **kwargs):
        tk.Canvas.__init__(self, master, bg="#4d4d4d", **kwargs)
        self.bar = self.create_rectangle(0, 0, 0, 9999, fill="#1db954", outline="#1db954")

    def set_progress_percentage(self, percentage: float):
        self.itemconfig(self.bar, width=percentage * self.winfo_width() * 2)


class FadedText(tk.Canvas):
    text: int

    def __init__(self, master: "SpotifyRemoteWindow", width, font=("Verdana", 11), **kwargs):
        tk.Canvas.__init__(self, master, width=width, **kwargs)
        self.text = self.create_text(0, 0, anchor=tk.NW, font=font)
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
            "device_icon": a("device.png"),
            "fade": a("fade.png")
        }

        self.title("Spotify Remote UI")
        self.geometry("%dx%d" % size)

        # Playback controls
        self.play_btn = CleanButton(self)
        self.play_btn.place(
            x=(width - Sizing.PLAY_BUTTON_SIZE) // 2,
            y=height - Sizing.PLAY_BUTTON_SIZE - Sizing.SPACE_UNIT,
            width=Sizing.PLAY_BUTTON_SIZE,
            height=Sizing.PLAY_BUTTON_SIZE
        )
        self.update()
        self.set_playing_status(False)

        self.prev_btn = CleanButton(self, image=self.assets["prev_icon"])
        self.prev_btn.place(
            x=(0.5 * width - Sizing.SIDE_BUTTON_SIZE) // 2,
            y=height - Sizing.SIDE_BUTTON_SIZE - Sizing.SPACE_UNIT - (
                        Sizing.PLAY_BUTTON_SIZE - Sizing.SIDE_BUTTON_SIZE) // 2,
            width=Sizing.SIDE_BUTTON_SIZE,
            height=Sizing.SIDE_BUTTON_SIZE
        )
        self.update()

        self.next_btn = CleanButton(self, image=self.assets["next_icon"])
        self.next_btn.place(
            x=(1.5 * width - Sizing.SIDE_BUTTON_SIZE) // 2,
            y=self.prev_btn.winfo_y(),
            width=Sizing.SIDE_BUTTON_SIZE,
            height=Sizing.SIDE_BUTTON_SIZE
        )
        self.update()

        # Timestamps and progress bar
        self.timestamp_current = tk.Label(self, text="0:00", anchor=tk.W, font=("Verdana", 14))
        self.timestamp_current.place(
            x=Sizing.SPACE_UNIT,
            y=self.play_btn.winfo_y() - Sizing.TIMESTAMP_LABEL_HEIGHT,
            width=width // 2 - Sizing.SPACE_UNIT,
            height=Sizing.TIMESTAMP_LABEL_HEIGHT
        )
        self.update()

        self.timestamp_duration = tk.Label(self, text="0:00", anchor=tk.E, font=("Verdana", 14))
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
        self.device_icon = tk.Label(image=self.assets["device_icon"])
        self.device_icon.place(x=Sizing.SPACE_UNIT, y=Sizing.SPACE_UNIT)
        self.update()

        self.device_label = FadedText(
            self,
            font=("Verdana", 24, "bold"),
            width=width - self.device_icon.winfo_x() - self.device_icon.winfo_width() - Sizing.SPACE_UNIT
        )
        self.device_label.place(
            x=self.device_icon.winfo_x() + self.device_icon.winfo_width() + Sizing.SPACE_UNIT,
            y=self.device_icon.winfo_y(),
            height=self.device_icon.winfo_height()
        )
        self.update()

        # Cover image and song info
        self.current_cover_image_sequence = None
        self.current_cover_image_url = None

        self.cover_image = tk.Label()
        cover_image_y = self.device_icon.winfo_y() + self.device_icon.winfo_height() + Sizing.SPACE_UNIT
        self.cover_image_size = height - cover_image_y - (height - self.progress_bar.winfo_y()) - Sizing.SPACE_UNIT
        self.cover_image.place(
            x=Sizing.SPACE_UNIT,
            y=cover_image_y,
            width=self.cover_image_size,
            height=self.cover_image_size
        )

    def on_cover_loaded(self, event):
        self.unbind_all(self.current_cover_image_sequence)
        self.current_cover_image_sequence = None
        self.cover_image.configure(image=self.cover_image_stream)

    def set_playing_status(self, is_playing: bool):
        self.play_btn.configure(image=self.assets["pause_icon" if is_playing else "play_icon"])

    def set_progress_bar_value(self, percentage: float):
        self.progress_bar.set_progress_percentage(percentage)

    def set_timestamps(self, current: str, duration: str):
        self.timestamp_current.configure(text=current)
        self.timestamp_duration.configure(text=duration)

    def set_device_label(self, label: str):
        self.device_label.update_text(label)

    def set_cover_image(self, url: str):
        if self.current_cover_image_url == url:
            return

        if self.current_cover_image_sequence is not None:
            self.unbind_all(self.current_cover_image_sequence)

        self.current_cover_image_sequence = f"<<Image{url}Loaded>>"
        self.bind(self.current_cover_image_sequence, self.on_cover_loaded)
        Thread(target=get_cover_image_for_window, args=(self, url, self.cover_image_size)).start()
