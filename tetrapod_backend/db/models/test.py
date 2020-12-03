from .. import model
import logging

_LOGGER = logging.getLogger()


class test:
    def __init__(self, collection_name): 
        _LOGGER.info("[init] test model")
        self.model = model.model(collection_name)

    def _insert(self, doc):
        _LOGGER.info("inserting... 1")
        _LOGGER.info(f"{doc}")
        res = self.model.insert_one(doc)
        _LOGGER.info(res)
        return 0