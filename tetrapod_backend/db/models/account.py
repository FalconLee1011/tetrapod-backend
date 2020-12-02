from ..import model
import logging
class Account:
    def __init__(self,collection_name):
        logging.getLogger()._LOGGER.info("[init]Account")
        self.model = model.model(collection_name)
    def _get(self,doc):
        logging.getLogger()._LOGGER.info("getting... ")
        logging.getLogger()._LOGGER.info(f"{doc}")
        user = self.model.find_one(doc)
        logging.getLogger()._LOGGER.info(user)
        return user

    def _update(self,filter,update):
        logging.getLogger()._LOGGER.info("updating... ")
        logging.getLogger()._LOGGER.info(f"{filter}")
        res = self.model.find_one_and_update(filter,update)
        logging.getLogger()._LOGGER.info(res)
        return 0

    def _validate(self,doc):
        logging.getLogger()._LOGGER.info("validating... ")
        logging.getLogger()._LOGGER.info(f"{doc}")
        return 0

    def _new(self,doc):
        logging.getLogger()._LOGGER.info("inserting... ")
        logging.getLogger()._LOGGER.info(f"{doc}")
        res = self.model.insert_one(doc)
        logging.getLogger()._LOGGER.info(res)
        return 0

