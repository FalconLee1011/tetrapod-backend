from ..import model
from ...lib import config
import logging, jwt
_LOGGER = logging.getLogger()

class Notification:
    def __init__(self):
        _LOGGER.info("[init] Notification")
        self.model = model.model('notification')

    def _mapOne(self, rDocument):
        rDocument["_id"] = str(rDocument["_id"])
        return rDocument

    def _map(self, rDocuments):
        for (i, doc) in enumerate(rDocuments):
            rDocuments[i]["_id"] = str(doc["_id"])
        return rDocuments

    def get(self, doc, ifNone={}):
        _LOGGER.info("getting... ")
        _LOGGER.info(f"{doc}")
        rDocument = [self.model.find_one(doc)]
        _LOGGER.info(rDocument)
        if(rDocument == [None]): return ifNone
        return list(map(self._mapOne, rDocument))[0]

    def getMany(self, doc):
        res = [self.model.find(doc)]
        _LOGGER.info(res)
        return list(map(self._map, res))

    # def new(self,user,doc):
    def new(self, doc):
        _LOGGER.info("inserting... ")
        _LOGGER.info(f"{doc}")
        # res = self.model.update_one(user, {"$set": doc})
        res = self.model.insert_one(doc)
        _LOGGER.info(res)
        return 0
        # return str(res.documentIds[0])

    def redact(self, _id, doc):
        _LOGGER.info("redacting... ")
        _LOGGER.info(f"{doc}")
        res = self.model.update_one({"_id": _id}, {"$set": doc})
        _LOGGER.info(res)
        return 0
        # return str(res.documentIds[0])

    # - RESERVED FOR FUTER UPDATE
    # def delete(self,doc):
    #     _LOGGER.info("deleting... ")
    #     _LOGGER.info(f"{doc}")
    #     res = self.model.delete_one(doc)
    #     _LOGGER.info(res)
    #     return 0