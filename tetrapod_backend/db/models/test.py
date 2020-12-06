from .. import model
import logging

_LOGGER = logging.getLogger()

COLLECTION_NAME = "test__"

class test:
    def __init__(self): 
        _LOGGER.info("[init] test model")
        self.model = model.model(COLLECTION_NAME)

    def _insert(self, doc):
        _LOGGER.info("inserting... 1")
        _LOGGER.info(f"{doc}")
        res = self.model.insert_one(doc)
        _LOGGER.info(res)
        return 0

    def _insert_many(self, doc):
        _LOGGER.info(f"inserting... {len(doc)}")
        _LOGGER.info(f"{doc}")
        res = self.model.insert_many(doc)
        _LOGGER.info(res)
        return 0
