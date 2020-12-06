from ..db.models import merchant, account
from ..lib import config
from .app import *
import jwt
import json

@app.route("/upload_merchant",methods=["POST"])
@account.Account.validate
def _upload_merchant():
    # get form ,pop token
    form=request.get_json()
    secret = config.getConfig().get("app",{}).get("secret",None)
    _token = form.get("token",None)
    _account = jwt.decode(_token,secret).get("account",None)

    form.pop('token',None)
    form["account"]=_account
    json.dumps(form)
    #insert merchant db
    MODEL = merchant.Merchant()
    MODEL.new(form)
    return make_response(jsonify("upload merchant seccess"),200)

    # POST
    # "price":"4129889",
    # "photo":"",
    # "merchant_name":"textbook",
    # "count":"20",
    # "discription":"It's a book",
    # "is_bidding":"0",
    # "bidding_price":"",
    # "bidding_price_perbid":"",
    # "bidding_endtime":"",
    # "token": ""

    # to DB
    # "account":"aaaaa"
    # "price":"4129889",
    # "photo":"",
    # "merchant_name":"textbook",
    # "count":"20",
    # "discription":"It's a book",
    # "is_bidding":"0",
    # "bidding_price":"",
    # "bidding_price_perbid":"",
    # "bidding_endtime":""