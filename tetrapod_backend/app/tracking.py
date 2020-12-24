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
    r = []
    for i in _bsh:
        if(type(i)!=dict):
            MODEL_account.update(_account,{'$pull':{'browsing_history': i}})
        else:
            try:
                r.append([i['merchant_id'],i['date']])
            except:
                # MODEL_account.update(_account,{'$pull':{'browsing_history': i}})
                return make_response({"Error": "db type error"}, 404)
    if  len(r) != 0:
        r = sorted(r,key = lambda x:x[1],reverse=True)
        res = []
        for i in r:
            try:
                res.append(MODEL_merchant.getOne({"_id":ObjectId(i[0])}))
            except:
                return make_response({"Error": "db type error"}, 404)
        return make_response({"browsing_history": res}, 200)
    else: return make_response({"browsing_history": None}, 404)