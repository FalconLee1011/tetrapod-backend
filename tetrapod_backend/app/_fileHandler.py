from .app import *
from uuid import uuid1
from ..lib import config
from uuid import uuid1
from os import path
import logging, io

_LOGGER = logging.getLogger()
ROOT_PATH = config.getConfig().get("filehandler", {}).get("root_path", "/cache")

class _fileHandler():
    def save(self, files):
        successCount = 0
        uuids = []
        if(len(files) == 0): return None
        else:
            for file in files:
                try:
                    splitted = file.filename.split(".")
                    filename = f'{str(uuid1())}.{splitted[len(splitted) - 1]}'
                    fullFileName = path.join(ROOT_PATH, filename)
                    file.save(fullFileName)
                    _LOGGER.info(f"[INFO] Writting file '{fullFileName}'.")
                    uuids.append(filename)
                    successCount += 1
                except Exception as err:
                    _LOGGER.error(f"[ERROR] Following error has occured while saving file '{file.filename}'.")
                    _LOGGER.error(err)
                    return uuids
        _LOGGER.info(f"[INFO] Successfuly saved {successCount} of {len(files)} files.")
        return uuids

    def get(self, uuid):
        file = None
        try:
            fullFileName = path.join(ROOT_PATH, uuid)
            with open(fullFileName, 'rb') as f:
                _LOGGER.info(f"[INFO] Reading file '{fullFileName}'.")
                file = io.BytesIO(f.read())
        except Exception as err:
            _LOGGER.error(f"[ERROR] Following error has occured while reading file '{uuid}'.")
            _LOGGER.error(err)
        return file