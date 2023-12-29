import time


def seconds_to_timestamp(seconds: int):
    minutes = seconds // 60
    seconds = seconds % 60

    return f"{minutes}:{seconds:02d}"


def unix_millis() -> int:
    return int(round(time.time() * 1000))
