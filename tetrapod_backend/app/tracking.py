from ..db.models import account, merchant
from .app import *
from bson.objectid import ObjectId

MODULE_PREFIX = '/tracking'
MODEL_account = account.Account()
MODEL_merchant = merchant.Merchant()

@app.route(f"{MODULE_PREFIX}/browsing_history",methods=["GET"])
@account.Account.validate
def _browsing_history(*args,**kwargs):
    _account = kwargs['account']
    _account = MODEL_account.get({"account":_account})
    _bsh = _account['browsing_history']
    res = []
    for i in _bsh:
        try:
            m = MODEL_merchant.getOne({"_id":ObjectId(i)})
            res.append(m)
        except:
            account.Account().update(_account,{'$pull':{'browsing_history': i}})
    if  len(res) != 0: return make_response({"browsing_history": res}, 200)
    else: return make_response({"browsing_history": None}, 404)