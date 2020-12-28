# 

from ..import model
from ...lib import config
import logging, jwt
from functools import wraps
from flask import request,make_response,jsonify
_LOGGER = logging.getLogger()

class ActiveUsers:
    def __init__(self):
        _LOGGER.info("[init] ActiveUsers")
        self.model = model.model('active_users')

    def _mapOne(self, rDocument):
        rDocument["_id"] = str(rDocument["_id"])
        return rDocument

    def _map(self, rDocuments):
        for (i, doc) in enumerate(rDocuments):
            rDocuments[i]["_id"] = str(doc["_id"])
        return rDocuments

    def get(self, doc):
        _LOGGER.info("getting... ")
        _LOGGER.info(f"{doc}")
        rDocument = [self.model.find_one(doc)]
        _LOGGER.info(rDocument)
        if(rDocument != [None]): return list(map(self._mapOne, rDocument))[0]
        else: return None

    def activateUser(self,user,doc):
        _LOGGER.info(f" Activating user session... {doc}")
        _LOGGER.info(f"{doc}")
        res = self.model.update_one(user, {"$set": doc})
        _LOGGER.info(res)
        return res

    def deactivateUser(self,doc):
        _LOGGER.info(f" Deactivating user session... {doc}")
        _LOGGER.info(f"{doc}")
        res = self.model.delete_one(doc)
        _LOGGER.info(res)
        return 0
