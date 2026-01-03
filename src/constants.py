import subprocess as _sub

_startupinfo = _sub.STARTUPINFO()
_startupinfo.dwFlags |= _sub.STARTF_USESHOWWINDOW

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
