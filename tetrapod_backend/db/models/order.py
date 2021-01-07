from ..import model
from ...lib import config
import logging, jwt
from flask import request,make_response,jsonify
_LOGGER = logging.getLogger()

class Order:
    def __init__(self):
        _LOGGER.info("[init] Order")
        self.model = model.model('order')

    def getOne(self, doc):
        _LOGGER.info("getting... ")
        _LOGGER.info(f"{doc}")
        rDocument = [self.model.find_one(doc)]
        _LOGGER.info(rDocument)
        def _map(rDocument):
            rDocument["_id"] = str(rDocument["_id"])
            return rDocument
        return list(map(_map, rDocument))[0]

    def getMultiple(self, doc, sort=[]):
        _LOGGER.info("getting... ")
        _LOGGER.info(f"{doc}")
        rDocuments = self.model.find(doc, mSort=sort)
        _LOGGER.info(rDocuments)
        def _map(rDocument):
            rDocument["_id"] = str(rDocument["_id"])
            return rDocument
        return list(map(_map, rDocuments))

    def update(self,filter,update):
        _LOGGER.info("updating... ")
        _LOGGER.info(f"{filter}")
        res = self.model.find_one_and_update(filter,update)
        _LOGGER.info(res)
        return 0

    def new(self,doc):
        _LOGGER.info("inserting... ")
        _LOGGER.info(f"{doc}")
        res = self.model.insert_one(doc)
        return str(res.documentIds[0])
        return 0

    def delete(self,doc):
        _LOGGER.info("deleting... ")
        _LOGGER.info(f"{doc}")
        res = self.model.delete_one(doc)
        _LOGGER.info(res)
        return 0