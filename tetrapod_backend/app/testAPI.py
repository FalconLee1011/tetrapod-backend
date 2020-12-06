from .app import *
from ..db.models import test

MODEL = test.test()

@app.route("/insert")
def _test_insert():
    status = MODEL._insert({"msg": "hello!"})
    return make_response(jsonify({"message": status}), 200)

@app.route("/test22")
def ___test2():
    MODEL._insert({
        "TEST": 0,
        "TEST1": 1
    })
    MODEL._insert_many(
        [
            {
                "TEST": 2,
                "TEST1": 3
            },
            {
                "TEST": 4,
                "TEST1": 5
            },
            {
                "TEST": 6,
                "TEST1": 7
            },
        ]
    )
    return make_response(jsonify({"message": "OK!"}), 200)
    