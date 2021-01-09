from ..db.models import merchant, account, order
from ..lib import config
from .app import *
from bson.objectid import ObjectId
from ._fileHandler import _fileHandler
import jwt, time, json, re, datetime
from flask import send_file
import pymongo, logging

MODULE_PREFIX = '/merchant'
MODEL = merchant.Merchant()
MODEL_ORDER = order.Order()
FILE_HANDLER = _fileHandler()
_LOGGER = logging.getLogger()
CONF = config.getConfig()


@app.route(f"{MODULE_PREFIX}/upload",methods=["POST"])
@account.Account.validate
def _upload_merchant(*args,**kwargs):
    # return make_response(jsonify("SERVICE MAINTENANCE"), 503)
    _price = int(request.form.get('price',0))
    _photo = FILE_HANDLER.save(files=request.files.getlist("files[]"))
    _merchant_name = request.form.get('name',"")
    _count = int(request.form.get('quantity',0))
    _discription = request.form.get('intro',"")
    _is_bidding = request.form.get('bidding_or_not',False)
    _is_bidding = True if(_is_bidding.lower() == "true") else False
    _status = request.form.get('new_or_not',"")
    _bidding_price = int(request.form.get('bidding_price',0))
    _bidding_price_perbid = int(request.form.get('bidding_price_perbid',0))
    _bidding_endtime = int(request.form.get('bidding_endtime',0))
    _account=kwargs['account']

    if _price < 1:
        return make_response(jsonify({"status": '價格異常'}), 422)

    if _photo == None:
        _photo = []
    
    if _count < 1:
        return make_response(jsonify({"status": '數量異常'}), 422)

    if _is_bidding == True:
        if _bidding_price < 1:
            return make_response(jsonify({"status": '競標價格異常'}), 422)
        
        if _bidding_price_perbid < 1:
            return make_response(jsonify({"status": '每標價格異常'}), 422)
        
        if _bidding_endtime - int(datetime.datetime.now().timestamp()) < 86400:
            return make_response(jsonify({"status": '競標時間異常'}), 422)

    form = {
        "price": _price,
        "photo": _photo,
        "merchant_name": _merchant_name,
        "count": _count,
        "discription": _discription,
        "is_bidding": _is_bidding,
        "bidding_price": _bidding_price,
        "bidding_price_perbid": _bidding_price_perbid,
        "bidding_endtime": _bidding_endtime,
        "account": _account,
        "status": _status,
        "winner_id": ""
    }
    MODEL = merchant.Merchant()
    MODEL.new(form)
    return make_response(jsonify("upload merchant success"),200)
    # return make_response(jsonify(form),200)

@app.route(f"{MODULE_PREFIX}/delete_merchant", methods=["POST"])
@account.Account.validate
def _delete_merchant():
    data = request.get_json()
    _merchant_id = data.get("merchant_id", "")
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
    data = request.form
    _merchant_id = data.get("merchant_id", "")
    _merchant = MODEL.getOne({"_id": ObjectId(_merchant_id)})
    _price = int(data.get('price', _merchant["price"]))
    _photo = FILE_HANDLER.save(files=request.files.getlist("files[]"))
    if _photo == None:
        _photo = _merchant["photo"]
    _merchant_name = data.get('name',_merchant["merchant_name"])
    _count = int(data.get('quantity',_merchant["count"]))
    _discription = data.get('intro',_merchant["discription"])

    Err = ""
    if _merchant_id == "":
        Err = "no merchant_id"
        return make_response(jsonify({"status": Err}),200)

    if _price < 1:
        return make_response(jsonify({"status": '價格異常'}), 422)
    
    if _count < 1:
        return make_response(jsonify({"status": '數量異常'}), 422)
    
    #make json
    form = {
        "price":_price,
        "photo":_photo,
        "merchant_name":_merchant_name,
        "count":_count,
        "discription":_discription,
    }
    f = {"_id": ObjectId(_merchant_id)}
    MODEL.update(f, {"$set":form})
    return make_response(jsonify("edit merchant success"),200)

@app.route(f"{MODULE_PREFIX}/get", methods=["GET", "POST"])
def _get_merchant():
    if(request.method == "GET"):
        mID = request.args.get("id")
        res = MODEL.getOne({"_id": ObjectId(mID)})
        if res != None: return make_response({"merchant": res}, 200)
        else: return make_response({"merchant": None}, 404)
    elif(request.method == "POST"):
        doc = request.get_json().get("query", {})
        res = MODEL.getMultiple(doc, sort=[("_created", pymongo.DESCENDING)])
        if res != [None]: return make_response({"merchants": res}, 200)
        else: return make_response({"merchants": None}, 404)

@app.route(f"{MODULE_PREFIX}/search", methods=["POST"])
def _search():
    keywords = request.get_json().get("keyword", None)
    _keywords = ""
    if(keywords):
        # _keywords = []
        # for keyword in keywords.split(" "): 
            # _keywords.append(keyword)
        _keywords = keywords.replace(" ", "|")
        _LOGGER.debug(keywords)
        _LOGGER.debug(_keywords)
        res = MODEL.getMultiple({"merchant_name": {"$regex": _keywords}})
        return make_response({"merchants": res}, 200)
    return make_response({"keys": _keywords}, 503)

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
    mID = request.get_json().get('merchant_id',None)
    _accountEntity = account.Account().get({'account':_act})
    _cart = _accountEntity.get("cart", None)
    merchantToBeAdd = MODEL.getOne({"_id": ObjectId(mID)})
    if _cart != None: 
        existingObj = next((merchant for merchant in _cart if merchant["merchant_id"] == mID), False)
        if(existingObj): # ADDING EXISTING COUNT
            existingMarchantIndex = _cart.index(existingObj)
            _cart[existingMarchantIndex]["merchant_count"] += 1
        else: # ADDING NEW IF NOT EXIST
            if(merchantToBeAdd):
                _cart.append(
                    {
                        "merchant_id": mID, 
                        "merchant_count": 1
                    }
                )
            else: 
                return make_response({"status": "Merchant does not exist"}, 400)
    account.Account().update(
        { "account": _act }, 
        { "$set": { "cart": _cart } }
    )
    return make_response({"status": "added", "merchant": merchantToBeAdd}, 200)

@app.route(f"{MODULE_PREFIX}/bidding/bid",methods=["POST"])
@account.Account.validate
def _bid(*args,**kwargs):
    data = request.get_json()
    _account = kwargs['account']
    _merchant_id = data.get("merchant_id", None)
    _bid_amount = int(data.get("bid_amount", None))
    if _merchant_id == "":
        Err = "no merchant_id"
        return make_response(jsonify({"status": Err}),200)
    if _bid_amount < 1 or _bid_amount > 1000000:
        Err = "amount error"
        return make_response(jsonify({"status": Err}),200)
    f = {"_id": ObjectId(_merchant_id)}
    _merchant_data = MODEL.getOne(f)
    _bidding_price = int(_merchant_data["bidding_price"]) + int(_bid_amount) * int(_merchant_data["bidding_price_perbid"])
    if(_bidding_price >= int(_merchant_data["price"])):
        _bidding_price = int(_merchant_data["price"])
    up = {
        "bidding_price": _bidding_price,
        "winner_id": _account
    }
    MODEL.update(f, {"$set":up})
    return make_response(jsonify("ok"),200)

@app.route(f"{MODULE_PREFIX}/bidding/bid_update",methods=["POST"])
@account.Account.validate
def _bid_update(*args,**kwargs):
    data = request.get_json()  
    _merchant_id = data.get("merchant_id", None)
    if _merchant_id == "":
        Err = "no merchant_id"
        return make_response(jsonify({"status": Err}),200)
    f = {"_id": ObjectId(_merchant_id)}
    merchant_data = MODEL.getOne(f)
    return make_response({"bidding price":merchant_data["bidding_price"]}, 200)

@app.route(f"{MODULE_PREFIX}/bidding/get_winner",methods=["POST"])
@account.Account.validate
def _get_winner(*args,**kwargs):
    def _is_expired(_cmp):
        _now = datetime.datetime.now().timestamp()
        if int(_cmp) < int(_now):
            return False
        else:
            return True
    
    def _add(_af, _merchant_id):
        _winner = account.Account().get(_af)
        if _winner["cart"] == None:
            _winner["cart"] = []
        account.Account().update(_af, {"$push": {"merchant_id":_merchant_id, "merchant_count":1}})
    data = request.get_json()
    _merchant_id = data.get("merchant_id", None)
    if _merchant_id == "":
        Err = "no merchant_id"
        return make_response(jsonify({"status": Err}),200)
    f = {"_id": ObjectId(_merchant_id)}
    _merchant_data = MODEL.getOne(f)
    if _merchant_data["winner_id"] == None:
        return make_response({"status": "nobody bid"}, 200)
    _af = {"account": _merchant_data["winner_id"]}
    _winner = account.Account().get(_af)
    #一口價
    if(int(_merchant_data["bidding_price"]) >= int(_merchant_data["price"])):
        _add(_af, _merchant_id)
        return make_response({"winner": _winner["account"]}, 200)
    _end_time = _merchant_data["bidding_endtime"]
    #超時
    if _is_expired(_end_time):
        return make_response({"status": "not yet"}, 200)
    _add(_af, _merchant_id)
    return make_response({"winner":_winner["account"]}, 200)

@app.route(f"{MODULE_PREFIX}/get_cart", methods=["GET"])
@account.Account.validate
def _get_cart(*args,**kwargs):
    _act = kwargs['account']
    _cart = account.Account().get({'account':_act}).get("cart", None)
    _LOGGER.debug('=========== CART ===========')
    _LOGGER.debug(_cart)
    _LOGGER.debug('=========== CART ===========')
    _rtnDoc = []
    if(_cart != None):
        for merch in _cart:
            mID = merch.get('merchant_id')
            merchQuery = requests.get(
                f"http://localhost:{CONF.get('app', {}).get('port')}/merchant/get?id={mID}"
            ).content
            merchObj = json.loads(merchQuery).get("merchant")
            merchObj["merchant_id"] = mID
            merchObj["merchant_count"] = merch.get('merchant_count')
            _rtnDoc.append(merchObj)
        return make_response({"merchants": _rtnDoc}, 200)    
    return make_response({"merchants": None}, 200)

@app.route(f"{MODULE_PREFIX}/get-cart-by-market", methods=["POST"])
@account.Account.validate
def _get_cart_by_market(*args,**kwargs):
    _act = kwargs['account']
    _target = request.get_json().get("market", "")
    _cart = account.Account().get({'account':_act}).get("cart", None)
    _rtnDoc = []
    if(_cart != None):
        for merch in _cart:
            mID = merch.get('merchant_id')
            merchQuery = requests.get(
                f"http://localhost:{CONF.get('app', {}).get('port')}/merchant/get?id={mID}"
            ).content
            merchObj = json.loads(merchQuery).get("merchant")
            if(merchObj.get("account") != _target): continue
            merchObj["merchant_id"] = mID
            merchObj["merchant_count"] = merch.get('merchant_count')
            _rtnDoc.append(merchObj)
        return make_response({"merchants": _rtnDoc}, 200)    
    return make_response({"merchants": None}, 200)


@app.route(f"{MODULE_PREFIX}/delete_cart", methods=["POST"])
@account.Account.validate
def _del_cart(*args,**kwargs):
    _act = kwargs['account']
    mID = request.get_json().get('merchant_id',None)
    try:
        account.Account().update({'account':_act,'cart.merchant_id':mID},{"$pull":{'cart':{"merchant_id":mID}}})
    except Exception as e:
        return make_response({"Error":"not found"}, 404)
    return make_response({"status":"delete success"}, 200)

@app.route(f"{MODULE_PREFIX}/edit_cart", methods=["POST"])
@account.Account.validate
def _edit_cart(*args,**kwargs): # can't tell whether merchant in cart
    _act = kwargs['account']
    mID = request.get_json().get('merchant_id',None)
    mcount = int(request.get_json().get('merchant_count',None))
    _gtm = MODEL.getOne({'_id':ObjectId(mID)})
    _getmercount = int(_gtm['count'])
    _getmerbid = _gtm['is_bidding']
    if mcount == 0:# del from cart
        try:
            account.Account().update({'account':_act,'cart.merchant_id':mID},{"$pull":{'cart':{"merchant_id":mID}}})
            return make_response({"status":"delete success"}, 200)
        except Exception as e:
            return make_response({"Error":"not found"}, 404)
    else:
        if mcount > _getmercount:# over the merchant count
            return make_response({"Error":"over the merchant count"},404)
        elif _getmerbid:# is bidding
            return make_response({"Error":"can't edit bidding merchant"},404)
        else:
            try:
                account.Account().update({'account':_act,'cart.merchant_id':mID},{"$set":{'cart.$.merchant_count':mcount}})
                return make_response({"merchant id":mID,"merchant count":mcount}, 200)
            except Exception as e:
                return make_response({"Error":"db error"}, 404)
    return make_response({"Error":"nothing happend"}, 200)
