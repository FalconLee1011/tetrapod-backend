from ..import model
from ...lib import config
import logging, jwt
from functools import wraps
from flask import request,make_response,jsonify

_LOGGER = logging.getLogger()

class Merchant:
    def __init__(self):
        _LOGGER.info("[init]Merchant")
        self.model = model.model('merchant')
    def get(self,doc):
        _LOGGER.info("getting... ")
        _LOGGER.info(f"{doc}")
        user = self.model.find_one(doc)
        _LOGGER.info(user)
        return user

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
        _LOGGER.info(res)
        return 0

    def delete(self,doc):
        _LOGGER.info("deleting... ")
        _LOGGER.info(f"{doc}")
        res = self.model.delete_one(doc)
        _LOGGER.info(res)
        return 0