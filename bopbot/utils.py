import os
import uuid
import json
import logging
from pythonjsonlogger import jsonlogger


class JsonLog:
    def __init__(self, name):
        self.name = name
        self.level = logging.DEBUG
        self.default_formatter = self.get_formatter()
        self.logger = logging.getLogger(self.name)

    def get_formatter(self):
        default_format = " ".join(
            ["(asctime)", "(levelname)", "(lineno)", "(funcName)", "(message)"]
        )

        return jsonlogger.JsonFormatter(default_format)

    def get_file_handler(self):
        file_path = f"{self.name}.json"
        with open(file_path, "w"):
            pass

        handler = logging.FileHandler(filename=file_path)
        handler.setFormatter(fmt=self.default_formatter)

        return handler

    def get_stream_handler(self):
        handler = logging.StreamHandler()

        return handler

    def build(self):
        self.logger.addHandler(hdlr=self.get_file_handler())
        self.logger.addHandler(hdlr=self.get_stream_handler())
        self.logger.setLevel(level=self.level)

        return self


def get_logger(name):
    return JsonLog(name=name).build().logger


def create_path(path):
    try:
        os.makedirs(path, exist_ok=True, mode=0o777)
    except Exception:
        raise


def load_json(path):
    with open(f"{path}.json", "r") as fl:
        return json.load(fl)


def dump_json(data, filename: str = None):
    if not filename:
        filename = uuid.uuid4()

    with open(f"{filename}.json", "w") as fl:
        json.dump(data, fl)
