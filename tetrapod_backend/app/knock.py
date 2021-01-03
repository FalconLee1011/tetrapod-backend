from .app import *
from ..db.models.account import Account
from ..lib import config
from ..db.models import knock, activeUsers, account
from json import loads
from bson.objectid import ObjectId

import logging
import jwt

_LOGGER = logging.getLogger()
MODEL = knock.Knock()
MODEL_ACTIVE_USERS = activeUsers.ActiveUsers()
MODEL_USERS = account.Account()

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

@app.route(f'{MODULE_PREFIX}/createRoom', methods=["POST"])
# @Account.validate 
def _createRoom():
    token = request.headers.get('token', None)
    account = jwt.decode(str.encode(token), CONF.get("app", {}).get("secret"), algorithms=["HS256"]).get("account")
    receiver = request.get_json().get("receiver", None);

    # Guard
    if(receiver == None):
        return make_response({"error": "cannot chat with someone called 'NULL'"}, 400)
    if(receiver == account):
        return make_response({"error": "are you this lone?"}, 400)
    
    existing_room = MODEL.get({"accounts": [account, receiver]})

    if(existing_room != None):
        return make_response({"room": existing_room.get("_id")}, 200)

    account_item = MODEL_USERS.get({"account": account})
    receiver_item = MODEL_USERS.get({"account": receiver})
    if(not account_item or not receiver_item): 
        return make_response({"error": "One of the account does not exist."}, 400)

    res = MODEL.new(
        {
            "accounts": [account, receiver],
            "messages": []
        }
    )
    receiver_doc = MODEL_ACTIVE_USERS.get({
        "account": receiver
    })
    if(receiver_doc != None):
        requests.post(
            "http://localhost:9001/io/notification/set-notify",
            json={
                "target": {
                    "type": "IOsession",
                    "target": receiver_doc.get("IOsession")
                },
                "content": f"You've been invited to chatroom {res}",
                "isBroadcast": False,
            }
        )

    MODEL_USERS.update({"account": account}, {"$push": {"knockroom": res}})
    MODEL_USERS.update({"account": receiver}, {"$push": {"knockroom": res}})

    return make_response({"room": res}, 200)

@app.route(f'{MODULE_PREFIX}/getRooms', methods=["POST"])
# @Account.validate 
def _getRooms():
    token = request.headers.get('token',None)
    _LOGGER.debug(f'GOT TOKEN {token}')
    account = jwt.decode(str.encode(token), CONF.get("app", {}).get("secret"), algorithms=["HS256"]).get("account")
    rooms = MODEL.getRoomWith({
        "account": account
    })[0]
    return make_response({"rooms": rooms}, 200)

@app.route(f'{MODULE_PREFIX}/getRoom', methods=["POST"])
# @Account.validate 
def _getRoom():
    roomID = request.get_json().get("roomID", None)
    room = MODEL.getRoom({"_id": ObjectId(roomID)})
    return make_response({"room": room}, 200)

@app.route(f'{MODULE_PREFIX}/newMessage', methods=["POST"])
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
    receiver = data.get('receiver', None)
    if(roomID == None): 
        _LOGGER.error("[ERROR] roomID not provided by sender")
        return
    if(message == None or message == ""): 
        _LOGGER.error("[ERROR] message is none or empty")
        return
    _LOGGER.debug(f"[debug] knock-io {request.remote_addr} : IO session ID: {IOsessionID} validating {token} ")
    tokenIsValid = _token_validation(token)
    _LOGGER.debug(f"[debug] knock-io {request.remote_addr} : IO session ID: {IOsessionID} with {token} valid -> {tokenIsValid} is sending message to room {roomID}")
    account = jwt.decode(str.encode(token), CONF.get("app", {}).get("secret"), algorithms=["HS256"]).get("account")
    
    msg = {"sender": account, "message": message, "timestamp": time(), "roomID": roomID}
    emit('newMessage', msg, room=roomID)

    # receiver_doc = MODEL_ACTIVE_USERS.get({
    #     "account": receiver
    # })
    # if(receiver_doc != None):
    requests.post(
        "http://localhost:9001/io/notification/set-notify",
        json={
            "target": {
                "type": "account",
                "target": receiver
            },
            "content": f"[{account}] {message}"
        }
    )

    res = loads(
        requests.post(
            f"http://localhost:{CONF.get('app', {}).get('port')}/knock/newMessage",
            json = {
                "message": msg,
                "roomID": roomID
            }
        ).content
    ).get("result")
    
@io.on('test', namespace=F"{IO_MODULE_PREFIX}")
def _tests(data):
    IOsessionID = request.sid 
    _LOGGER.debug(f"[debug] knock-io {request.remote_addr} : IO session ID: {IOsessionID}")
    _LOGGER.info(f"[info] knock-io: {request.remote_addr} : {data}")
    emit('test', {"servertime": time()})