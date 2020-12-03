from ..import model
import logging, jwt

_LOGGER = logging.getLogger()

class Token:
    def __init__(self):
        _LOGGER.info("[init]token")
        self.model = model.model('token')

    def get(self,doc):
        _LOGGER.info("getting token... ")
        _LOGGER.info(f"{doc}")
        user = self.model.find_one(doc)
        _LOGGER.info(user)
        return user

    def update(self,filter,update):
        _LOGGER.info("updating token... ")
        _LOGGER.info(f"{filter}")
        res = self.model.find_one_and_update(filter,update)
        _LOGGER.info(res)
        return 0

    def new(self,doc):
        _LOGGER.info("inserting token... ")
        _LOGGER.info(f"{doc}")
        res = self.model.insert_one(doc)
        _LOGGER.info(res)
        return 0