import subprocess as _sub

_startupinfo = _sub.STARTUPINFO()
_startupinfo.dwFlags |= _sub.STARTF_USESHOWWINDOW


class _Colors:
    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    orange = (255, 165, 0)
    yellow = (255, 255, 0)
    white = (255, 255, 255)
    black = (0, 0, 0)
    gray = (128, 128, 128)
    light_gray = (200, 200, 200)


colors = _Colors()

APP_NAME = "BluetoothMonitor"
SUBPROCESS_ARGS = {
    "startupinfo": _startupinfo,
    "creationflags": _sub.CREATE_NO_WINDOW,
    "text": True,
    "encoding": "utf-8",
    "capture_output": True,
}


class DeviceNotFoundError(Exception):
    pass


class DeviceNotConnectedError(Exception):
    pass
