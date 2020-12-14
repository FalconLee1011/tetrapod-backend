from ..db.models import account,token
from .app import *

@app.route("/logout",methods=["POST"])
@account.Account.validate
def _logout(*args, **kwargs):
    token_MODEL = token.Token()
    token_MODEL.update({"account":kwargs["account"]},{"$set":{"token":None}})
    return make_response(jsonify({"status":"ok"}),200)