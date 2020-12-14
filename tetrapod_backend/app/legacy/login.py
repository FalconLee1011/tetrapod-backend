from ..db.models import account,token
from .app import *
from ..lib import config
import time, jwt

@app.route("/login",methods=["POST"])
def _login():
    _account = request.get_json().get("account",None)
    _password = request.get_json().get("password",None)
    account_MODEL = account.Account()
    token_MODEL = token.Token()
    account_req = account_MODEL.get({"account":_account})
    if account_req != None and _account == account_req['account'] and _password == account_req['password']:
        token_req = token_MODEL.get({"account":_account})
        secret = config.getConfig().get("app",{}).get("secret")
        account_token = bytes.decode(jwt.encode({"account":_account,"timestamp":str(time.time())},secret))
        if token_req == None:
            token_MODEL.new({"account":_account,"token":account_token})
        else:    
            token_MODEL.update({"account":_account},{"$set": {"token": account_token}})
        return make_response(jsonify({"token":account_token}),200)
    return make_response(jsonify("login failure"), 401)