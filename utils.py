def seconds_to_timestamp(seconds: int):
    minutes = seconds // 60
    seconds = seconds % 60

    return f"{minutes}:{seconds:02d}"
