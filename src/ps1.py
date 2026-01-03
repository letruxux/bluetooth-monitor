import subprocess
import os
import sys
from constants import SUBPROCESS_ARGS, DeviceNotFoundError


def script_path(rel):
    base = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base, rel)


def run_ps(file: str, input: str) -> str:
    ps = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            script_path(os.path.join("scripts", file)),
        ],
        input=input,
        **SUBPROCESS_ARGS,
    )

    if ps.returncode != 0:
        raise RuntimeError(f"powershell error: {ps.stderr}")

    return ps.stdout.strip()


def find_instance_id(friendly_name: str) -> str:
    iid = run_ps("get.ps1", friendly_name)
    if not iid:
        raise DeviceNotFoundError(f"device not found: {friendly_name}")

    return iid


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
