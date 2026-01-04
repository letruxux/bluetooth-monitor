from constants import APP_NAME
import zon as zod
import typing
import json
import os

CONFIG_DIR = os.path.join(os.getenv("APPDATA"), APP_NAME)
os.makedirs(CONFIG_DIR, exist_ok=True)

config_schema = zod.record(
    {
        "version": zod.number(),
        "devices": zod.element_list(zod.string()),
        "check_interval": zod.number(),
    }
)

default_config = config_schema.validate(
    {
        "version": 1,
        "devices": [],
        "check_interval": 30,
    }
)

""" migration syustem """
""" migrations FROM version to the next """
migrations: dict[int, typing.Callable[[dict], dict]] = {}


class ConfigData:
    _raw: dict
    devices: list[str]
    check_interval: int

    def __init__(self, _raw: dict):
        self._raw = _raw
        self.devices = _raw["devices"]
        self.check_interval = _raw["check_interval"]


class _Config:
    def __init__(self):
        self.config_file = os.path.join(CONFIG_DIR, "config.json")
        self.data: dict | None = None
        self.load()

    def _write_config(self, data: dict):
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        self.data = data

    def load(self) -> ConfigData:
        if self.data is None:
            if not os.path.exists(self.config_file):
                data = config_schema.validate(default_config)
                self._write_config(data)
            else:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    self.data = config_schema.validate(json.load(f))
        return ConfigData(self.data)

    def save(self):
        if self.data is None:
            raise RuntimeError("config not loaded")
        self._write_config(self.data)


config = _Config()
