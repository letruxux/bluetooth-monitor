import pystray
from PIL import Image, ImageDraw
import time
import threading
import subprocess
import os
import sys
from tkinter import messagebox

APP_NAME = "BluetoothMonitor"

startupinfo = subprocess.STARTUPINFO()
startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW


def resource_path(rel):
    base = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base, rel)


def read_devices():
    appdata = os.getenv("APPDATA")
    programdir = os.path.join(appdata, APP_NAME)
    devices_file = os.path.join(programdir, "devices.txt")
    if not os.path.exists(devices_file):
        os.makedirs(programdir, exist_ok=True)
        open(devices_file, "w").write(
            "\n".join(
                [
                    "Device name 1",
                    "# change these with your devices, one per line.",
                ]
            )
        )
        messagebox.showerror(
            "Device names missing",
            "Please config your devices, close to open the configuration file.",
        )
        subprocess.run(
            ["notepad", f'"{devices_file}"'],
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW,
            text=True,
            encoding="utf-8",
            capture_output=True,
        )
        sys.exit(1)
    with open(devices_file, "r") as f:
        return [
            line.strip()
            for line in f.readlines()
            if (not line.strip().startswith("#")) and len(line.strip()) > 0
        ]


DEVICES = read_devices()


def run_ps(file: str, input: str) -> str:
    ps = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            resource_path(os.path.join("scripts", file)),
        ],
        input=input,
        text=True,
        encoding="utf-8",
        capture_output=True,
        startupinfo=startupinfo,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )

    if ps.returncode != 0:
        raise RuntimeError(f"powershell error: {ps.stderr}")

    return ps.stdout.strip()


def find_instance_id(friendly_name: str) -> str:
    return run_ps("get.ps1", friendly_name)


def get_battery_level(
    *, friendly_name: str | None = None, instance_id: str | None = None
) -> int:
    if friendly_name and instance_id:
        raise ValueError("pass either friendly_name or instance_id, not both")

    if not friendly_name and not instance_id:
        raise ValueError("you must pass friendly_name or instance_id")

    if friendly_name:
        instance_id = find_instance_id(friendly_name)

    return int(run_ps("battery.ps1", instance_id))


# ui ---------------------------
def on_exit_all():
    global running
    running = False
    for icon in icons:
        icon.stop()


icons: list = []
threads: list[threading.Thread] = []

menu = pystray.Menu(
    pystray.MenuItem("Exit", lambda icon, item: on_exit_all()),
)


def create_battery_icon(percentage):
    """
    Creates a dynamic icon representing the battery level.
    """
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

    # Draw battery body
    dc.rectangle((10, 10, 54, 60), outline=(255, 255, 255), width=3)
    # Draw battery tip
    dc.rectangle((22, 3, 42, 10), fill=(255, 255, 255))

    if percentage is not None:
        # Fill from bottom up
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

        time.sleep(30)


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
    for name in DEVICES:
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
