from ..db.models import merchant, account
from ..lib import config
from .app import *
from bson.objectid import ObjectId
from ._fileHandler import _fileHandler
import jwt, time, json, re, datetime
from flask import send_file
import pymongo

MODULE_PREFIX = '/merchant'
MODEL = merchant.Merchant()
FILE_HANDLER = _fileHandler()

@app.route(f"{MODULE_PREFIX}/upload",methods=["POST"])
@account.Account.validate
def _upload_merchant(*args,**kwargs):
    photos = FILE_HANDLER.save(files=request.files.getlist("files[]"))
    # return make_response(jsonify("SERVICE MAINTENANCE"), 503)
    _price = request.form.get('price',None)
    _photo = photos
    _merchant_name = request.form.get('name',None)
    _count = request.form.get('quantity',None)
    _discription = request.form.get('intro',None)
    _is_bidding = request.form.get('bidding_or_not',False)
    _status = request.form.get('new_or_not',None)
    _bidding_price = request.form.get('bidding_price',None)
    _bidding_price_perbid = request.form.get('bidding_price_perbid',None)
    _bidding_endtime = request.form.get('bidding_endtime',None)

    _account=kwargs['account']

    match = re.match(r"[1-9][0-9]*", _price)
    if not(match):
        return make_response(jsonify({"status": '價格異常'}), 422)

    match = re.match(r"[1-9][0-9]*", _count)
    if not(match):
        return make_response(jsonify({"status": '數量異常'}), 422)

    # match = re.match(r"[0-1]", _is_bidding)
    # if not(match):
    #     return make_response(jsonify({"status": '競標狀態異常'}), 422)

    # elif(_is_bidding=='1'):
    #     match = re.match(r"[1-9][0-9]*", _bidding_price)
    #     if not(match):
    #         return make_response(jsonify({"status": '競標價格異常'}), 422)

    #     match = re.match(r"[1-9][0-9]*", _bidding_price_perbid)
    #     if not(match):
    #         return make_response(jsonify({"status": '每標價格異常'}), 422)

    #     try:
    #         match_bidding_endtime = datetime.datetime.strptime(_bidding_endtime,"%Y-%m-%d%H:%M")
    #         _now = datetime.datetime.now()
    #         if(match_bidding_endtime < _now):
    #             return make_response(jsonify({"status": '競標時間異常'}), 422)
    #     except:
    #         return make_response(jsonify({"status": '競標時間異常'}), 422)
    # else:
    #     _bidding_price = None
    #     _bidding_price_perbid = None
    #     _bidding_endtime = None
    #make json
    _is_bidding = True if(_is_bidding.lower() == "true") else False
    form = {
        "price": _price,
        "photo": _photo,
        "merchant_name": _merchant_name,
        "count": _count,
        "discription": _discription,
        "is_bidding": bool(_is_bidding),
        "bidding_price": _bidding_price,
        "bidding_price_perbid": _bidding_price_perbid,
        "bidding_endtime": _bidding_endtime,
        "account": _account,
        "status": _status,
    }
    MODEL = merchant.Merchant()
    MODEL.new(form)
    return make_response(jsonify("upload merchant success"),200)
    # return make_response(jsonify(form),200)

@app.route(f"{MODULE_PREFIX}/delete_merchant", methods=["POST"])
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

@app.route(f"{MODULE_PREFIX}/edit_merchant", methods=["POST"])
@account.Account.validate
def _edit_merchant(*args,**kwargs):
    data = request.get_json()
    _merchant_id = data.get("merchant id", "")
    _price = data.get('price',None)
    _photo = data.get('photo',None)
    _merchant_name = data.get('merchant_name',None)
    _count = data.get('count',None)
    _discription = data.get('discription',None)
    _is_bidding = data.get('is_bidding',None)
    _bidding_price = data.get('bidding_price',None)
    _bidding_price_perbid = data.get('bidding_price_perbid',None)
    _bidding_endtime = data.get('bidding_endtime',None)
    _account = kwargs['account']

    Err = ""
    if _merchant_id == "":
        Err = "no merchant_id"
        return make_response(jsonify({"status": Err}),200)

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

        # Note: Disabled for demo
        # try:
        #     match_bidding_endtime = datetime.datetime.strptime(_bidding_endtime,"%Y-%m-%d%H:%M")
        #     _now = datetime.datetime.now()
        #     if(match_bidding_endtime < _now):
        #         return make_response(jsonify({"status": '競標時間異常'}), 422)
        # except:
        #     return make_response(jsonify({"status": '競標時間異常'}), 422)
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
    f = {"_id": ObjectId(_merchant_id)}
    MODEL.update(f, {"$set":form})
    return make_response(jsonify("edit merchant success"),200)

def _Browsing_history(mID):
    _tk = request.headers.get('token',None)
    if(_tk): #token exist
        _srt = config.getConfig().get("app",{}).get("secret")
        _act = jwt.decode(str.encode(_tk),_srt)['account']
        _bhisnull = account.Account().get({'account':_act})['browsing_history']
        if _bhisnull != None: #history exist
            _bh = account.Account().get({'$and':[{'account':_act},{'browsing_history': mID}]})
            if _bh == None: # del old
                account.Account().update({"account":_act},{'$push': {'browsing_history': mID}})
            else:
                account.Account().update(_bh,{'$pull':{'browsing_history': mID}})
                account.Account().update({"account":_act},{'$push': {'browsing_history': mID}})
        else:
            account.Account().update({"account":_act},{'$set': {'browsing_history': [mID]}})
    else:
        return

@app.route(f"{MODULE_PREFIX}/get", methods=["GET"])
def _get_merchant():
    mID = request.args.get("id")
    _Browsing_history(mID)
    res = MODEL.getOne({"_id": ObjectId(mID)})
    if res != None: return make_response({"merchant": res}, 200)
    else: return make_response({"merchant": None}, 404)

@app.route(f"{MODULE_PREFIX}/getall", methods=["GET"])
def _get_allmerchants():
    mID = request.args.get("id")
    res = MODEL.getMultiple({}, sort=[("_created", pymongo.DESCENDING)])
    if len(res) != 0: return make_response({"merchants": res}, 200)
    else: return make_response({"merchants": None}, 404)

@app.route(f"{MODULE_PREFIX}/add_to_cart", methods=["POST"])
@account.Account.validate
def _add_to_cart(*args,**kwargs):
    _act = kwargs['account']
    mID = request.get_json().get('merchant id',None)
    _cart = account.Account().get({'account':_act,'cart':{"$type":"array"}})
    _ct = 1
    if _cart != None: #cart type correct
        _ce = account.Account().get({'$and':[{'account':_act},{'cart':{"$elemMatch":{"merchant_id":mID}}}]})
        if _ce == None:# new
            account.Account().update({"account":_act},{'$push': {'cart': {"merchant_id":mID,"merchant_count":1}}})
        else:# old plus
            _mct = _ce['cart']
            for i in _mct:
                try:
                    if i['merchant_id'] == mID:
                        _ct = i['merchant_count']
                        break
                except:
                    return make_response({"Error": "db type error"}, 404)
            _ct += 1
            account.Account().update({"account":_act,"cart.merchant_id":mID},{'$set': {'cart.$.merchant_count': _ct}})
    else:
        account.Account().update({"account":_act},{'$set': {'cart':[{"merchant_id":mID,"merchant_count":1}]}})
    return make_response({"merchant_id": mID,"merchant_count":_ct}, 200)