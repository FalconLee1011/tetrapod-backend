from ..db.models import account
from .app import *
from ..lib import config
import  re, jwt, random, string, logging
from time import time
from flask_mail import Message
from ..lib.config import getConfig
from threading import Thread

_LOGGER = logging.getLogger()

MODULE_PREFIX = '/accounts'
MODEL = account.Account()

@app.route(f"{MODULE_PREFIX}/get", methods=["POST"])
def _get_account():
    account = request.get_json().get("account")
    acc = MODEL.getWithRedacted({
        "account": account
    })
    return make_response({"account": acc}, 200)

@app.route(f"{MODULE_PREFIX}/get-user", methods=["POST"])
def _get_user():
    account = request.get_json().get("account")
    acc = MODEL.get({
        "account": account
    })
    return make_response({"account": acc}, 200)