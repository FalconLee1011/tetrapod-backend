from ..db.models import merchant, account
from ..lib import config
from .app import *
import jwt, time, json, re, datetime

@app.route("/upload_merchant",methods=["POST"])
@account.Account.validate
def _upload_merchant(*args,**kwargs):

    _price = request.get_json().get('price',None)
    _photo = request.get_json().get('photo',None)
    _merchant_name = request.get_json().get('merchant_name',None)
    _count = request.get_json().get('count',None)
    _discription = request.get_json().get('discription',None)
    _is_bidding = request.get_json().get('is_bidding',None)
    _bidding_price = request.get_json().get('bidding_price',None)
    _bidding_price_perbid = request.get_json().get('bidding_price_perbid',None)
    _bidding_endtime = request.get_json().get('bidding_endtime',None)
    _account=kwargs['account']

    match = re.match(r"[1-9][0-9]*", _price)
    if not(match):
        return make_response(jsonify({"status": '價格異常'}), 422)

    match = re.match(r"[1-9][0-9]*", _count)
    if not(match):
        return make_response(jsonify({"status": '數量異常'}), 422)

    match = re.match(r"[0-1]", _is_bidding)
    if not(match):
        return make_response(jsonify({"status": '競標狀態異常'}), 422)

    elif(_is_bidding=='1'):
        match = re.match(r"[1-9][0-9]*", _bidding_price)
        if not(match):
            return make_response(jsonify({"status": '競標價格異常'}), 422)

        match = re.match(r"[1-9][0-9]*", _bidding_price_perbid)
        if not(match):
            return make_response(jsonify({"status": '每標價格異常'}), 422)

        try:
            match_bidding_endtime = datetime.datetime.strptime(_bidding_endtime,"%Y-%m-%d%H:%M")
            _now = datetime.datetime.now()
            if(match_bidding_endtime < _now):
                return make_response(jsonify({"status": '競標時間異常'}), 422)
        except:
            return make_response(jsonify({"status": '競標時間異常'}), 422)
    else:
        _bidding_price = None
        _bidding_price_perbid = None
        _bidding_endtime = None
    #make json
    form = {
        "price":_price,
        "photo":_photo,
        "merchant_name":_merchant_name,
        "count":_count,
        "discription":_discription,
        "is_bidding":_is_bidding,
        "bidding_price":_bidding_price,
        "bidding_price_perbid":_bidding_price_perbid,
        "bidding_endtime":_bidding_endtime,
        "account":_account
    }
    MODEL = merchant.Merchant()
    MODEL.new(form)
    return make_response(jsonify("upload merchant success"),200)

