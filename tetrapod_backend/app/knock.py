from .app import *
from ..db.models.account import Account
from ..lib import config
from ..db.models import knock, activeKnocks
from json import loads
from bson.objectid import ObjectId

import logging
import jwt

_LOGGER = logging.getLogger()
MODEL = knock.Knock()
# MODEL_ACTIVE_SESSIONS = activeKnocks.ActiveKnocks()

IO_MODULE_PREFIX = '/io'
MODULE_PREFIX = '/knock'

CONF = config.getConfig()

def _token_validation(token):
    return loads(
        requests.post(
            f"http://localhost:{CONF.get('app', {}).get('port')}/auth/validate",
            json = {
                "token": token
            }
        ).content
    ).get("result")

@app.route('/knock/createRoom', methods=["POST"])
# @Account.validate 
def _createRoom():
    token = request.headers.get('token', None)
    account = jwt.decode(str.encode(token), CONF.get("app", {}).get("secret"), algorithms=["HS256"]).get("account")
    res = MODEL.new(
        {
            "accounts": [account, "b"],
            "messages": []
        }
    )
    return make_response({"room": res}, 200)

@app.route('/knock/getRooms', methods=["POST"])
# @Account.validate 
def _getRooms():
    token = request.headers.get('token', None)
    account = jwt.decode(str.encode(token), CONF.get("app", {}).get("secret"), algorithms=["HS256"]).get("account")
    rooms = MODEL.getRoomWith({
        "account": account
    })
    return make_response({"rooms": rooms}, 200)

@app.route('/knock/getRoom', methods=["POST"])
# @Account.validate 
def _getRoom():
    roomID = request.get_json().get("roomID", None)
    room = MODEL.getRoom({"_id": ObjectId(roomID)})
    return make_response({"room": room}, 200)

@app.route('/knock/newMessage', methods=["POST"])
def _newMessage():
    if(request.remote_addr not in ["127.0.0.1", "localhost"]):
        return make_response("U bad teapot", 418)
    roomID = request.get_json().get("roomID", None)
    message = request.get_json().get("message", None)
    if(message == None): 
        return make_response(None, 200)
    msgs = MODEL.getRoom({"_id": ObjectId(roomID)}, proj=["messages"]).get("messages")
    _LOGGER.debug(f"[DEBUG] {msgs}")
    msgs.append(message)
    MODEL.newMessage({"_id": ObjectId(roomID)}, {"$set": {"messages": msgs}})
    return make_response({"room": roomID}, 200)

@io.on('connect', namespace=F"{MODULE_PREFIX}")
def _connect():
    IOsessionID = request.sid
    _LOGGER.info(f"[info] knock-io: {request.remote_addr} has connected with IO session ID {IOsessionID}")
    emit('connected', {"servertime": time()})

@io.on('knock-init', namespace=F"{IO_MODULE_PREFIX}")
def _knock_init(data):
    IOsessionID = request.sid
    token = data.get('token', None)
    roomID = data.get('roomID', None)
    if(roomID == None): 
        _LOGGER.error("[ERROR] roomID not provided by sender")
        return
    _LOGGER.debug(f"[debug] knock-io {request.remote_addr} : IO session ID: {IOsessionID} validating {token} ")
    tokenIsValid = _token_validation(token)
    _LOGGER.debug(f"[debug] knock-io {request.remote_addr} : IO session ID: {IOsessionID} with {token} valid -> {tokenIsValid}")
    account = jwt.decode(str.encode(token), CONF.get("app", {}).get("secret"), algorithms=["HS256"]).get("account")
    join_room(roomID)
    emit('activeRoom', {"account": account, "room": rooms(roomID)}, room=roomID)

@io.on('knock-send', namespace=F"{IO_MODULE_PREFIX}")
def sendMessage(data):
    IOsessionID = request.sid
    token = data.get('token', None)
    roomID = data.get('roomID', None)
    message = data.get('message', None)
    if(roomID == None): 
        _LOGGER.error("[ERROR] roomID not provided by sender")
        return
    _LOGGER.debug(f"[debug] knock-io {request.remote_addr} : IO session ID: {IOsessionID} validating {token} ")
    tokenIsValid = _token_validation(token)
    _LOGGER.debug(f"[debug] knock-io {request.remote_addr} : IO session ID: {IOsessionID} with {token} valid -> {tokenIsValid} is sending message")
    account = jwt.decode(str.encode(token), CONF.get("app", {}).get("secret"), algorithms=["HS256"]).get("account")
    
    msg = {"sender": account, "message": message, "timestamp": time()}
    emit('message', msg, room=roomID)

    res = loads(
        requests.post(
            f"http://localhost:{CONF.get('app', {}).get('port')}/knock/newMessage",
            json = msg
        ).content
    ).get("result")
    

@io.on('test', namespace=F"{IO_MODULE_PREFIX}")
def _tests(data):
    IOsessionID = request.sid 
    _LOGGER.debug(f"[debug] knock-io {request.remote_addr} : IO session ID: {IOsessionID}")
    _LOGGER.info(f"[info] knock-io: {request.remote_addr} : {data}")
    emit('test', {"servertime": time()})