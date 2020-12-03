from ..db.models import account
from .app import *
from ..lib import config
import time
import jwt

@app.route("/login",methods=["POST"])
def _login():
    _account = request.get_json().get("account",None)
    _password = request.get_json().get("password",None)
    MODEL = account.Account()
    req = MODEL.get({"account":_account})
    secret = config.getConfig().get("app",{}).get("secret")
    token = bytes.decode(jwt.encode({"account":_account,"timestamp":str(time.time())},secret))
    MODEL.update({"account":_account},{"$set": {"token": token}})
    if req != None and _account == req['account'] and _password == req['password']:
        return make_response(jsonify({"token":token}),200)
    return make_response(jsonify("login failure"), 401)