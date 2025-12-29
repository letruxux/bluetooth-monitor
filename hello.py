import pystray
from PIL import Image, ImageDraw
import time
import threading
import subprocess
import os

BATTERY_KEY = "{104EA319-6EE2-4701-BD47-8DDBF425BBE5} 2"
FRIENDLY_NAME = "Crusher Evo"


def run_ps(file: str, input: str) -> str:
    ps = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            os.pat.join(os.path.dirname(__file__), "scripts", file),
        ],
        input=input,
        text=True,
        encoding="utf-8",
        capture_output=True,
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


def get_battery_info():
    """
    Bridge between the synchronous thread and the asynchronous WinSDK call.
    """
    try:
        level = get_battery_level(friendly_name=FRIENDLY_NAME)

        return FRIENDLY_NAME, level
    except:
        return "Not Connected", None


# --- UI LOGIC ---


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


# --- CONTROL LOGIC ---

running = True


def update_loop(icon):
    global running
    while running:
        name, battery = get_battery_info()

        # Update the icon image and tooltip
        icon.icon = create_battery_icon(battery)
        if battery is not None:
            icon.title = f"{name}: {battery}%"
        else:
            icon.title = "Device not found / disconnected"

        time.sleep(30)  # Check every 30 seconds


def on_exit(icon, item):
    global running
    running = False
    icon.stop()


# --- MAIN ---

menu = pystray.Menu(
    pystray.MenuItem("Exit", on_exit),
)

icon = pystray.Icon(
    "BluetoothMonitor",
    create_battery_icon(None),
    title="Searching...",
    menu=menu,
)

if __name__ == "__main__":
    # Start the background thread
    t = threading.Thread(target=update_loop, args=(icon,))
    t.daemon = True
    t.start()

    try:
        icon.run()
    except KeyboardInterrupt:
        running = False
        icon.stop()
