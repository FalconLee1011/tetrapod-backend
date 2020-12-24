from flask import Flask, Blueprint, jsonify, request, make_response, send_file
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
from flask_mail import Mail
from flask_cors import CORS
from time import time
from ..lib import config
import requests

app = Flask(__name__)
app.debug = config.getConfig().get("app", {}).get('debug', False)
io = SocketIO(app, cors_allowed_origins="*")
mail = None
CORS(app=app)

def init_mail():
    global mail 
    mail = Mail(app)
    return

def get_mail():
    return mail

@app.route("/test")
def _test():
    return make_response(jsonify({"message": "Hello There!"}), 200)

@io.on('connect', namespace="/io")
def _connect():
    print(f"{request.remote_addr} has connected !")
    emit('connected', {"servertime": time()})

# if __name__ == "__main__":
#     io.run(app, host="0.0.0.0", port="")