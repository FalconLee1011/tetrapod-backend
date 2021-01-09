from ..db.models import account, merchant
from .app import *
from bson.objectid import ObjectId
import jwt, logging

MODULE_PREFIX = '/tracking'
MODEL_account = account.Account()
MODEL_merchant = merchant.Merchant()

_LOGGER = logging.getLogger()

CONF = config.getConfig()

@app.route(f"{MODULE_PREFIX}/browsing-history/get",methods=["GET"])
@account.Account.validate
def _get_browsing_history(*args,**kwargs):
    _account = kwargs['account']
    history = MODEL_account.get({"account":_account}, _proj=["browsing_history"])
    return make_response({"history": history}, 200)

@app.route(f"{MODULE_PREFIX}/browsing-history/push",methods=["GET"])
def _push_browsing_history():
    token = request.headers.get('token', None)
    mID = request.args.get("merchantid")
    _account = jwt.decode(str.encode(token), CONF.get("app", {}).get("secret"), algorithms=["HS256"]).get("account")
    history = MODEL_account.get({"account":_account}, _proj=["browsing_history"]).get("browsing_history")
    try: history.remove(mID)
    except: _LOGGER.debug(f"HISTORY DOES NOT EXIST")
    history.append(mID)
    # _LOGGER.debug(f"\033[38;5;10m HISTORY UPDATED --------> {history}")

    MODEL_account.update(
        { "account": _account },
        {
            "$set": {
                "browsing_history": history
            }
        }
    )
    return "updated"
    