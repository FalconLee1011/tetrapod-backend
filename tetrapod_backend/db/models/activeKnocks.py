# 
# ! UNUSED BUT RESERVED FOR DEVELOPMENT

from ..import model
from ...lib import config
import logging, jwt
from functools import wraps
from flask import request,make_response,jsonify
_LOGGER = logging.getLogger()

class ActiveKnocks:
    def __init__(self):
        _LOGGER.info("[init] ActiveKnocks")
        self.model = model.model('active_knocks')

    def _mapOne(self, rDocument):
        rDocument["_id"] = str(rDocument["_id"])
        return rDocument

    def _map(self, rDocuments):
        for (i, doc) in enumerate(rDocuments):
            rDocuments[i]["_id"] = str(doc["_id"])
        return rDocuments

    def getSession(self, doc):
        _LOGGER.info("getting... ")
        _LOGGER.info(f"{doc}")
        rDocument = [self.model.find_one(doc)]
        _LOGGER.info(rDocument)
        if(rDocument != [None]): return list(map(self._mapOne, rDocument))[0]
        else: return None

    def getRoomWith(self, doc):
        _LOGGER.info(f"getting rooms for {doc.get('account')}")
        res = [
            self.model.find(
                {
                    "accounts": { "$in": [doc.get('account')] }
                },
                mProject=["_id", "accounts"]
            )
        ]
        _LOGGER.info(res)
        return list(map(self._map, res))
    
    def getRoom(self, doc):
        _LOGGER.info(f"getting rooms where {doc}")
        res = [self.model.find_one(doc)]
        _LOGGER.info(res)
        return list(map(self._mapOne, res))

    def update(self,filter,update):
        _LOGGER.info("updating... ")
        _LOGGER.info(f"{filter}")
        res = self.model.find_one_and_update(filter,update)
        _LOGGER.info(res)
        return 0

    def createSession(self,doc):
        _LOGGER.info(f"creating knock session... {doc}")
        _LOGGER.info(f"{doc}")
        res = self.model.insert_one(doc)
        _LOGGER.info(res)
        return str(res.documentIds[0])

    def clearSession(self,doc):
        _LOGGER.info("deleting... ")
        _LOGGER.info(f"{doc}")
        res = self.model.delete_one(doc)
        _LOGGER.info(res)
        return 0