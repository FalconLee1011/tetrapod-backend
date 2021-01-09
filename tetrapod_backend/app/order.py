from ..db.models import merchant, account, order
from ..lib import config
from .app import *
from bson.objectid import ObjectId
from ._fileHandler import _fileHandler
import jwt, time, json, re, datetime
from flask import send_file
import pymongo, logging

MODULE_PREFIX = '/merchant/order'
MODEL = merchant.Merchant()
MODEL_ORDER = order.Order()
FILE_HANDLER = _fileHandler()
_LOGGER = logging.getLogger()
CONF = config.getConfig()

@app.route(f"{MODULE_PREFIX}/new-order", methods=["POST"])
@account.Account.validate
def _new_order(*args,**kwargs): # can't tell whether merchant in cart
    _account = kwargs['account']
    rq = request.get_json()
    merchQuery = requests.post(
        f"http://localhost:{CONF.get('app', {}).get('port')}/merchant/get-cart-by-market",
        json={ "market": rq.get("market") },
        headers={ "token": request.headers.get("token") }
    ).content
    _merchants = json.loads(merchQuery).get("merchants")
    _merchIDs = []
    price = 0
    order = {
        "merchants": [],
        "buyer": _account,
        "market": rq.get("market"),
        "shipment_method": rq.get("shipment"),
        "status":[
            { "status": "newed", "timestamp": time.time(), "is_done": True, },
            { "status": "confirmed", "timestamp": -1, "is_done": False },
            { "status": "contacted", "timestamp": -1, "is_done": False },
            { "status": "shipping", "timestamp": -1, "is_done": False },
            { "status": "doneShipping", "timestamp": -1, "is_done": False },
            { "status": "doneGatering", "timestamp": -1, "is_done": False },
        ],
        "cState": 0,
        "approve": False,
    }
    for _merch in _merchants:    
        price += (_merch.get("price") * int(_merch.get("merchant_count")))
        order["merchants"].append(_merch)
        _merchIDs.append(_merch.get("merchant_id"))
    order["price"] = price

    _ins = MODEL_ORDER.new(order)
    # _LOGGER.debug(_ins)

    account.Account().update(
        { "account": _account }, 
        { 
            "$pull": { 
                "cart": {
                    "merchant_id": {
                        "$in": _merchIDs
                    }
                }
            }
        }
    )
    return make_response({"status": "ok", "order_id": _ins}, 200)

@app.route(f"{MODULE_PREFIX}/get-orders/buyer", methods=["GET", "POST"])
@account.Account.validate
def _get_order_buyer(*args,**kwargs):
    _account = kwargs['account']
    if(request.method == "GET"):
        orders = MODEL_ORDER.getMultiple({ "buyer": _account }, sort=[("_created", pymongo.DESCENDING)])
        if(orders != [None] or orders != None):
            return make_response({"orders": orders}, 200)
    elif(request.method == "POST"):
        rq = request.get_json()
        try:
            order = MODEL_ORDER.getMultiple({ "_id": ObjectId(rq.get("orderID")) })
            if(order != None):
                return make_response({"order": order}, 200)
        except Exception as e:
            _LOGGER.error(e) 
    return make_response({"status": "error"}, 400)

@app.route(f"{MODULE_PREFIX}/get-orders/seller", methods=["GET", "POST"])
@account.Account.validate
def _get_order_seller(*args,**kwargs):
    _account = kwargs['account']
    if(request.method == "GET"):
        orders = MODEL_ORDER.getMultiple({ "market": _account }, sort=[("_created", pymongo.DESCENDING)])
        if(orders != [None] or orders != None):
            return make_response({"orders": orders}, 200)
    elif(request.method == "POST"):
        rq = request.get_json()
        try:
            order = MODEL_ORDER.getMultiple({ "_id": ObjectId(rq.get("orderID")) })
            if(order != None):
                return make_response({"order": order}, 200)
        except: pass
    return make_response({"status": "error"}, 400)

@app.route(f"{MODULE_PREFIX}/update-order", methods=["POST"])
@account.Account.validate
def _update_order(*args,**kwargs): # can't tell whether merchant in cart
    _account = kwargs['account']
    rq = request.get_json()
    act = rq.get('action')
    orderID = rq.get("orderID", "")
    cState = 0
    _order = MODEL_ORDER.getOne({"_id": ObjectId(orderID)})
    # _LOGGER.debug(f" \033[38;5;43m --------> doing {rq.get('action')} ON {_order}")
    _status = _order.get("status")
    # _LOGGER.debug(f" \033[38;5;43m STATUS --------> {_status}")
    approve = False

    if(act == 'rm'):
        if(_account != _order.get('market')): return make_response("action is not allowed", 403)
        _state = next((state for state in _status if state["status"] == "confirmed"), {})
        # _LOGGER.debug(f" \033[38;5;43m UPDATING --------> {_state}")
        cState = _status.index(_state)
        _status[cState]["timestamp"] = time.time()
        _status[cState]["is_done"] = True
        _status[cState]["status"] = "canceled"
    
    elif(act == 'ship'):
        if(_account != _order.get('market')): return make_response("action is not allowed", 403)
        _state = next((state for state in _status if state["status"] == "contacted"), {})
        # _LOGGER.debug(f" \033[38;5;43m UPDATING --------> {_state}")
        cState = _status.index(_state)
        _status[cState]["timestamp"] = time.time()
        _status[cState]["is_done"] = True
        _status[cState]["status"] = "contacted"

        _state = next((state for state in _status if state["status"] == "shipping"), {})
        cState = _status.index(_state)
        _status[cState]["timestamp"] = time.time()
        _status[cState]["is_done"] = True
        _status[cState]["status"] = "shipping"

    elif(act == 'cfn'):
        if(_account != _order.get('market')): return make_response("action is not allowed", 403)
        _state = next((state for state in _status if state["status"] == "confirmed"), {})
        # _LOGGER.debug(f" \033[38;5;43m UPDATING --------> {_state}")
        cState = _status.index(_state)
        _status[cState]["timestamp"] = time.time()
        _status[cState]["is_done"] = True
        approve = True

    elif(act == 'doneShipping'):
        if(_account != _order.get('market')): return make_response("action is not allowed", 403)
        _state = next((state for state in _status if state["status"] == "doneShipping"), {})
        # _LOGGER.debug(f" \033[38;5;43m UPDATING --------> {_state}")
        cState = _status.index(_state)
        _status[cState]["timestamp"] = time.time()
        _status[cState]["is_done"] = True
        _status[cState]["status"] = "doneShipping"

    elif(act == 'doneGatering'):
        if(_account != _order.get('buyer')): return make_response("action is not allowed", 403)
        _state = next((state for state in _status if state["status"] == "doneGatering"), {})
        # _LOGGER.debug(f" \033[38;5;43m UPDATING --------> {_state}")
        cState = _status.index(_state)
        _status[cState]["timestamp"] = time.time()
        _status[cState]["is_done"] = True
        _status[cState]["status"] = "doneGatering"

        
    # _LOGGER.debug(f" \033[38;5;10m ORDER UPDATED --------> {_order}")
    
    update = MODEL_ORDER.update(
        {"_id": ObjectId(orderID)}, 
        {"$set": {
                "status": _status, 
                "cState": cState,
                "approve": approve,
            }
        }
    )

    return make_response({"status": act}, 200)