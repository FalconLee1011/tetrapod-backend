from ..db.models import merchant, account
from .app import *
import json
from bson.objectid import ObjectId

@app.route("/delete_merchant", methods=["POST"])
@account.Account.validate

def _delete_merchant():
    data = request.get_json()
    _merchant_id = data.get("merchant id", "")
    Err = ""
    if _merchant_id == "":
        Err = "no merchant_id"
        return make_response(jsonify({"status": Err}),200)
    merchant_model = merchant.Merchant()
    f = {"_id": ObjectId(_merchant_id)}
    merchant_model.delete(f)
    return make_response(jsonify({"status": "ok"}),200)