from .app import *
from ..db.models.account import Account
from ..lib import config
from ..db.models import knock, activeUsers, notification
from json import loads
from bson.objectid import ObjectId

import logging
import jwt

_LOGGER = logging.getLogger()
MODEL = notification.Notification()
MODEL_ACTIVE_USERS = activeUsers.ActiveUsers()

IO_MODULE_PREFIX = 'io'
MODULE_PREFIX = 'notification'

CONF = config.getConfig()

@app.route(f"/{IO_MODULE_PREFIX}/{MODULE_PREFIX}/set-notify", methods=["POST"])
def _notify():
    target_session = None
    req = request.get_json()
    target = req.get("target", {})
    target_account = target.get("target")
    content = req.get("content", None)
    emitType = req.get("emitType", "toast")
    _broadcast = str(req.get("isBroadcast", "False"))
    _type = req.get("type", "info")

    broadcast = (_broadcast.lower() == "true")

    if(not broadcast and target.get("type") == "account"):
        target_doc = MODEL_ACTIVE_USERS.get({
            "account": target.get("target")
        })
        target_session = target_doc.get("IOsession")
    elif(not broadcast and target.get("type") == "sessionID"):
        target_session = target.get("target")

    _LOGGER.debug(f"[debug] io-notification: sending notification {content} to {target}, broadcast = {broadcast}")
    _notification = {
        "content": content,
        "type": _type,
        "emitType": emitType
    }
    io.emit(
        'notify',
        _notification,
        broadcast=broadcast, 
        to=target_session, 
        namespace="/io"
    )

    if(target.get("type") == "sessionID"):
        target_doc = MODEL_ACTIVE_USERS.get({
            "IOsession": target_session
        })
        target_account = target_doc.get("account")

    if(not broadcast):
        # history_notification = MODEL.get({"account": target_account}).get("notifications", [])
        # history_notification.append(_notification)
        MODEL.new(
            {
                "account": target_account, 
                "notifications": _notification
            }
        )
            
    elif(broadcast):
        # history_notification = MODEL.get({"account": target_account}).get("notifications", [])
        # history_notification.append(_notification)
        MODEL.new(
            {
                "account": "all", 
                "notifications": _notification
            }
        )

    return make_response(jsonify("Done"), 200)


@app.route(f"/{IO_MODULE_PREFIX}/{MODULE_PREFIX}/get-notify", methods=["GET"])
def _get_notify():
    _account = request.args.get("account")
    notifications = MODEL.getMany({"account": {"$in": [_account, "all"]}, "redact": {"$ne": True}})
    return make_response({"notifications": notifications[0]}, 200)

@app.route(f"/{IO_MODULE_PREFIX}/{MODULE_PREFIX}/redact-notify", methods=["GET"])
def _redact_notify():
    _id = request.args.get("id")
    MODEL.redact(ObjectId(_id), {"redact": True})
    return make_response(jsonify("Done"), 200)