from .app import *
from ..db.models.account import Account
from ..db.models.knock import Knock
from ..db.models.activeUsers import ActiveUsers 
from ..lib import config
from json import loads
from bson.objectid import ObjectId

import logging
import jwt

_LOGGER = logging.getLogger()
CONF = config.getConfig()

MODEL = Knock()
MODEL_ACCOUNT = Account()
MODEL_ACTIVE_USERS = ActiveUsers()

IO_MODULE_PREFIX = '/io'
MODULE_PREFIX = '/io'

@io.on('connect', namespace=F"{IO_MODULE_PREFIX}")
def _connect():
    IOsessionID = request.sid
    _LOGGER.info(f"[info] knock-io: {request.remote_addr} has connected with IO session ID {IOsessionID}")
    emit('connected')

@io.on('connect-init', namespace=F"{IO_MODULE_PREFIX}")
def _connect_init(data):
    IOsessionID = request.sid
    token = data.get('token', None)
    if(token != None):
        _account = jwt.decode(str.encode(token), CONF.get("app", {}).get("secret"), algorithms=["HS256"]).get("account")
        _doc = {
            "token": token,
            "account": _account,
            "IOsession": IOsessionID
        }
        MODEL_ACTIVE_USERS.activateUser(
            {
                "account": _account
            }, 
            _doc
        )
        _LOGGER.info(f"[info] io-service: {_doc} user activated.")
        join_room(IOsessionID)
    emit('inited', {"servertime": time(), "account": _account})

@io.on('disconnect', namespace=F"{IO_MODULE_PREFIX}")
def _disconnect():
    IOsessionID = request.sid
    _doc = {
        "IOsession": IOsessionID
    }
    MODEL_ACTIVE_USERS.deactivateUser(_doc)
    _LOGGER.info(f"[info] io-service: {_doc} user deactivated.")