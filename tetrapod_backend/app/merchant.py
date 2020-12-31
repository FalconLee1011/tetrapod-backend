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
        "winner_id": None
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
        _winner_id = None    
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
        "account":_account,
        "winner_id":_winner_id
    }
    
    MODEL = merchant.Merchant()
    f = {"_id": ObjectId(_merchant_id)}
    MODEL.update(f, {"$set":form})
    return make_response(jsonify("edit merchant success"),200)

def _Browsing_history(mID):
    _tk = request.headers.get('token',None)
    if(_tk): # token exist
        _srt = config.getConfig().get("app",{}).get("secret")
        _act = jwt.decode(str.encode(_tk),_srt)['account']
        _bhisnull = account.Account().get({'account':_act,'browsing_history':{"$type":"array"}})
        if _bhisnull != None: # history type correct
            _bh = account.Account().get({'$and':[{'account':_act},{'browsing_history':{"$elemMatch":{"merchant_id":mID}}}]})
            if _bh == None: # new
                account.Account().update({"account":_act},{'$push':{'browsing_history':{'merchant_id':mID,"date":datetime.datetime.now()}}})
            else:
                account.Account().update({"account":_act,'browsing_history.merchant_id':mID},{'$set': {'browsing_history.$.date':datetime.datetime.now()}})
        else:
            account.Account().update({"account":_act},{'$set': {'browsing_history':[{"merchant_id":mID,"date":datetime.datetime.now()}]}})
    else:
        return

@app.route(f"{MODULE_PREFIX}/get", methods=["GET", "POST"])
def _get_merchant():
    if(request.method == "GET"):
        mID = request.args.get("id")
        _Browsing_history(mID)
        res = MODEL.getOne({"_id": ObjectId(mID)})
        if res != None: return make_response({"merchant": res}, 200)
        else: return make_response({"merchant": None}, 404)
    elif(request.method == "POST"):
        doc = request.get_json().get("query", {})
        res = MODEL.getMultiple(doc, sort=[("_created", pymongo.DESCENDING)])
        if res != [None]: return make_response({"merchants": res}, 200)
        else: return make_response({"merchants": None}, 404)

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

@app.route(f"{MODULE_PREFIX}/bidding/bid",methods=["POST"])
@account.Account.validate
def _bid(*args,**kwargs):
    data = request.get_json()
    _account = kwargs['account']
    _merchant_id = data.get("merchant id", None)
    _bid_amount = int(data.get("bid amount", None))
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
    _merchant_id = data.get("merchant id", None)
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
        if float(_cmp) < float(_now):
            return False
        else:
            return True
    
    def _add(_af, _merchant_id):
        _winner = account.Account().get(_af)
        if _winner["cart"] == None:
            account.Account().update(_af, {"$set": {'cart':[{"merchant_id":_merchant_id, "merchant_count":1}]}})
        else:
            account.Account().update(_af, {"$push": {"merchant_id":_merchant_id, "merchant_count":1}})
    data = request.get_json()
    _merchant_id = data.get("merchant id", None)
    if _merchant_id == "":
        Err = "no merchant_id"
        return make_response(jsonify({"status": Err}),200)
    f = {"_id": ObjectId(_merchant_id)}
    _merchant_data = MODEL.getOne(f)
    if _merchant_data["winner_id"] == None:
        return make_response({"status": "nobody bid"}, 200)
    _af = {"account": _merchant_data["winner_id"]}
    _winner = account.Account().get(_af)
    if(int(_merchant_data["bidding_price"]) >= int(_merchant_data["price"])):
        _add(_af, _merchant_id)
        return make_response({"winner": _winner["account"]}, 200)
    _end_time = _merchant_data["bidding_endtime"]
    if _is_expired(_end_time):
        return make_response({"status": "not yet"}, 200)
    _add(_af, _merchant_id)
    return make_response({"winner":_winner["account"]}, 200)

@app.route(f"{MODULE_PREFIX}/get_cart", methods=["GET"])
@account.Account.validate
def _get_cart(*args,**kwargs):
    _act = kwargs['account']
    _cart = account.Account().get({'account':_act,'cart':{"$type":"array"}})
    _getmulct = []
    _getcount = []
    if _cart != None:# cart type correct
        for i in _cart['cart']:
            if(type(i)!=dict):
                account.Account().update(_act,{'$pull':{'cart': i}})
            else:
                try:
                    _getmulct.append(ObjectId(i['merchant_id']))
                    _getcount.append(i['merchant_count'])
                except:
                    pass
        if len(_getmulct)!=0:
            try:# get merchant and set count
                res = MODEL.getMultiple({"_id":{"$in":_getmulct}})
            except:
                return make_response({"Error": "db type error"}, 404)
            for zz in range(0,len(res)):
                res[zz]['merchant_count'] = _getcount[zz]
            return make_response({"merchants":res},200)    
    return make_response({"merchants": None}, 200)

@app.route(f"{MODULE_PREFIX}/delete_cart", methods=["POST"])
@account.Account.validate
def _del_cart(*args,**kwargs):
    _act = kwargs['account']
    mID = request.get_json().get('merchant id',None)
    try:
        account.Account().update({'account':_act,'cart.merchant_id':mID},{"$pull":{'cart':{"merchant_id":mID}}})
    except Exception as e:
        return make_response({"Error":"not found"}, 404)
    return make_response({"status":"delete success"}, 200)

@app.route(f"{MODULE_PREFIX}/edit_cart", methods=["POST"])
@account.Account.validate
def _edit_cart(*args,**kwargs): # can't tell whether merchant in cart
    _act = kwargs['account']
    mID = request.get_json().get('merchant id',None)
    mcount = int(request.get_json().get('merchant count',None))
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
