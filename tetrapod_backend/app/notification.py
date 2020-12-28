from .app import *
from ..db.models.account import Account
from ..lib import config
from ..db.models import knock, activeUsers
from json import loads
from bson.objectid import ObjectId

import logging
import jwt

_LOGGER = logging.getLogger()
MODEL = knock.Knock()
MODEL_ACTIVE_USERS = activeUsers.ActiveUsers()

IO_MODULE_PREFIX = 'io'
MODULE_PREFIX = 'notification'

CONF = config.getConfig()

@app.route(f"/{IO_MODULE_PREFIX}/{MODULE_PREFIX}/set-notify", methods=["POST"])
def _notify():
    target = request.get_json().get("target", None)
    target_session = target.get("target")
    content = request.get_json().get("content", None)
    broadcast = request.get_json().get("isBroadcast", "False")
    _type = request.get_json().get("type", "info")
    
    if(broadcast.lower() == "true"): broadcast = True
    else: broadcast = False

    if(target.get("type") == "account"):
        target_doc = MODEL_ACTIVE_USERS.get({
            "account": target.get("target")
        })
        target_session = target_doc.get("IOsession")

    _LOGGER.debug(f"[debug] io-notification: sending notification {content} to {target}, broadcast = {broadcast}")
    io.emit(
        'notify',
        {
            "content": content,
            "type": _type
        }, 
        broadcast=broadcast, 
        to=target_session, 
        namespace="/io"
    )
    return make_response(jsonify("Done"), 200)
