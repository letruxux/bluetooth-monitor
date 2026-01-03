import pystray
from PIL import Image, ImageDraw
import time
import threading
from constants import APP_NAME
from config import config
from ps1 import get_battery_level
from ctypes import windll

# yay its not in 240p anymore
windll.shcore.SetProcessDpiAwareness(1)

icons: list = []
threads: list[threading.Thread] = []

menu = pystray.Menu(
    pystray.MenuItem("Exit", lambda icon, item: on_exit_all()),
)


# ui ---------------------------
def on_exit_all():
    global running
    running = False
    for icon in icons:
        icon.stop()


def create_battery_icon(percentage):
    # thanks ai for whatever this is
    width, height = 64, 64
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    dc = ImageDraw.Draw(image)

    if percentage is None:
        color = (128, 128, 128)  # Gray
        fill_level = 0
    else:
        if percentage > 50:
            color = (0, 255, 0)  # Green
        elif percentage > 20:
            color = (255, 165, 0)  # Orange
        else:
            color = (255, 0, 0)  # Red
        fill_level = int((percentage / 100) * (height - 15))

    # body
    dc.rectangle((10, 10, 54, 60), outline=(255, 255, 255), width=3)
    # tip
    dc.rectangle((22, 3, 42, 10), fill=(255, 255, 255))

    if percentage is not None:
        # fill from bottom up
        bottom_y = 57
        top_y = max(13, bottom_y - fill_level)
        dc.rectangle((13, top_y, 51, bottom_y), fill=color)

    return image


# update ---------------------------

running = True


def update_loop(icon, friendly_name):
    global running
    while running:
        try:
            level = get_battery_level(friendly_name=friendly_name)
            icon.icon = create_battery_icon(level)
            icon.title = f"{friendly_name}: {level}%"
        except Exception as e:
            print(e)
            icon.icon = create_battery_icon(None)
            icon.title = f"{friendly_name}: not connected"

        time.sleep(config.load().check_interval)


def on_exit(icon, item):
    global running
    running = False
    icon.stop()


# --- MAIN ---

menu = pystray.Menu(
    pystray.MenuItem("Exit", on_exit),
)

icon = pystray.Icon(
    APP_NAME,
    create_battery_icon(None),
    title="Searching...",
    menu=menu,
)

if __name__ == "__main__":
    for name in config.load().devices:
        icon = pystray.Icon(
            name,
            create_battery_icon(None),
            title=f"{name}: searching...",
            menu=menu,
        )

        t = threading.Thread(
            target=update_loop,
            args=(icon, name),
            daemon=True,
        )

        icons.append(icon)
        threads.append(t)

        t.start()
        icon.run_detached()

    try:
        while running:
            time.sleep(1)
    except KeyboardInterrupt:
        on_exit_all()
