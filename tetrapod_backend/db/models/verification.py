from ..import model
import logging

_LOGGER = logging.getLogger()

class Verification:
    def __init__(self):
        _LOGGER.info("[init]verification")
        self.model = model.model('verification')

    def get(self,doc):
        _LOGGER.info("getting verification... ")
        _LOGGER.info(f"{doc}")
        user = self.model.find_one(doc)
        _LOGGER.info(user)
        return user

    def update(self,filter,update):
        _LOGGER.info("updating verification... ")
        _LOGGER.info(f"{filter}")
        res = self.model.find_one_and_update(filter,update)
        _LOGGER.info(res)
        return 0

    def new(self,doc):
        _LOGGER.info("inserting verification... ")
        _LOGGER.info(f"{doc}")
        res = self.model.insert_one(doc)
        _LOGGER.info(res)
        return 0

    def delete(self,doc):
        _LOGGER.info("deleting verification... ")
        _LOGGER.info(f"{doc}")
        res = self.model.delete_one(doc)
        _LOGGER.info(res)
        return 0