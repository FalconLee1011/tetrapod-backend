from ..import model
from ...lib import config
import logging, jwt
from functools import wraps
from flask import request,make_response,jsonify
from . import token
_LOGGER = logging.getLogger()

class Account:
    def __init__(self):
        _LOGGER.info("[init]Account")
        self.model = model.model('account')
    def get(self,doc,_proj=None):
        _LOGGER.info("getting account... ")
        _LOGGER.info(f"{doc}")
        user = self.model.find_one(doc, mProject=_proj)
        try: 
            del user["_id"]
        except: 
            _LOGGER.warning("User not found!")   
        _LOGGER.info(user)
        return user

    def getWithRedacted(self, doc):
        _LOGGER.info("getting account with redacted information... ")
        _LOGGER.info(f"{doc}")
        user = self.model.find_one(doc, mProject=[
            "account_avator", 
            "first_name", 
            "last_name", 
            "nick_name", 
            "account", 
            "market_description"
        ])
        try: 
            del user["_id"]
        except: 
            _LOGGER.warning("User not found!")    
        _LOGGER.info(user)
        return user

    def update(self,_filter,update):
        _LOGGER.info("updating account... ")
        _LOGGER.info(f"{_filter}")
        res = self.model.find_one_and_update(_filter,update)
        _LOGGER.info(res)
        return 0

    def validate(func):
        @wraps(func)
        def decorator(*args,**kwargs):
            front_token = request.headers.get('token',None)
            db_token = token.Token().get({"token":front_token})
            secret = config.getConfig().get("app",{}).get("secret")
            _LOGGER.info("validating token... ")
            if db_token != None and front_token != None and front_token != '' and front_token == db_token.get('token'):
                _LOGGER.info("Front token: "+front_token)
                _LOGGER.info("DB token: "+db_token.get('token'))
                try:
                    token_data = jwt.decode(str.encode(front_token), secret, algorithms=["HS256"])
                    kwargs = token_data
                    return func(*args,**kwargs)
                except Exception as e:
                    _LOGGER.error(e)
                    return make_response(jsonify("Invalid token"),401)
            return make_response(jsonify("Invalid token"),401)
        return decorator

    def new(self,doc):
        _LOGGER.info("inserting account... ")
        _LOGGER.info(f"{doc}")
        res = self.model.insert_one(doc)
        _LOGGER.info(res)
        return 0

