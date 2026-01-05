from constants import APP_NAME, colors, DeviceNotFoundError, DeviceNotConnectedError
from ps1 import get_battery_level, get_all_connected
from PIL import Image, ImageDraw
from tkinter import messagebox
from config import config
from ctypes import windll
import config_gui
import threading
import pystray
import time

# yay its not in 240p anymore
windll.shcore.SetProcessDpiAwareness(1)

icons: list = []
threads: list[threading.Thread] = []

menu = pystray.Menu(
    pystray.MenuItem("Settings", lambda icon, item: config_gui.open_config()),
    pystray.MenuItem("Exit", lambda icon, item: on_exit_all()),
)


# ui ---------------------------
def on_exit_all():
    global running
    running = False
    for icon in icons:
        icon.stop()


def create_battery_icon(percentage, fill_color=colors.white):
    # thanks ai for whatever this is
    width, height = 64, 64
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    dc = ImageDraw.Draw(image)

    if percentage is None:
        color = colors.gray  # Gray
        fill_level = 0
    else:
        if percentage > 50:
            color = colors.green  # Green
        elif percentage > 20:
            color = colors.orange  # Orange
        else:
            color = colors.red  # Red
        fill_level = int((percentage / 100) * (height - 15))

    # body
    dc.rectangle((10, 10, 54, 60), outline=fill_color, width=3)
    # tip
    dc.rectangle((22, 3, 42, 10), fill=fill_color)

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
            is_connected = friendly_name in get_all_connected()
            if not is_connected:
                raise DeviceNotConnectedError(f"device not connected: {friendly_name}")

            level = get_battery_level(friendly_name=friendly_name)
            icon.icon = create_battery_icon(level)
            icon.title = f"{friendly_name}: {level}%"
        except DeviceNotFoundError:
            icon.icon = create_battery_icon(None, colors.red)
            icon.title = f"{friendly_name}: not found"
        except DeviceNotConnectedError:
            icon.icon = create_battery_icon(None, colors.gray)
            icon.title = f"{friendly_name}: disconnected"
        except Exception:
            icon.icon = create_battery_icon(None)
            icon.title = f"{friendly_name}: unknown error"

        time.sleep(config.load().check_interval)


# --- MAIN ---


icon = pystray.Icon(
    APP_NAME,
    create_battery_icon(None),
    title="Searching...",
    menu=menu,
)

if __name__ == "__main__":
    if len(config.load().devices) == 0:
        config_gui.open_config()
        messagebox.showerror(
            "No devices found",
            "Please add at least one device to the config file and restart the app.",
        )
        exit()

    for name in config.load().devices:
        icon = pystray.Icon(
            name,
            create_battery_icon(None, colors.light_gray),
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
