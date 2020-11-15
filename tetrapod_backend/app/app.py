from flask import Flask, Blueprint, jsonify, request, make_response
from flask_socketio import SocketIO, emit
from time import time

app = Flask(__name__)
app.debug = True
io = SocketIO(app)

@app.route("/test")
def _test():
    return make_response(jsonify({"message": "Hello There!"}), 200)

@io.on('connect', namespace="/io")
def _connect():
    print(f"{request.remote_addr} has connected !")
    emit('connected', {"servertime": time()})

# if __name__ == "__main__":
#     io.run(app, host="0.0.0.0", port="")