from .app import *
from ..db.models import test

COLLECTION = "test_collection"

@app.route("/insert")
def _test_insert():
    MODEL = test.test(COLLECTION)
    status = MODEL._insert({"msg": "hello!"})
    return make_response(jsonify({"message": status}), 200)

@app.route("/test22")
def ___test2():
    return "test222222"