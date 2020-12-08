from ..db.models import account
from .app import *
from ..lib import config
import time
import jwt
import re
@app.route("/register",methods=["POST"])

def _register():
    def _len_check(s):
        if len(s) > 5 and len(s) < 21:
            return True
        else:
            return False

    def _different_password(str1, str2):
        if str1 == str2:
            return True
        else:
            return False

    def _is_match(s, pat):
        return re.match(pat, s)

    data = request.get_json()   
    _First_name = data.get("first name","")
    _Last_name = data.get("last name","")
    _Nick_name = data.get("nick name","")
    _account = data.get("account","")
    _password = data.get("password","")
    _confirm_password = data.get("confirm password","")
    _email = data.get("e-mail","")
    _phone = data.get("phone","")
    Pass = True
    Err = ""
    MODEL = account.Account()
    
    #account check 英文大小寫開頭+英數，至少6碼至多20碼
    req = MODEL.get({"account":_account})
    if req != None:
        Err = "account already exists"
        return make_response(jsonify({"status": Err}), 200)
    pattern = r"[a-zA-Z]+[a-zA-Z0-9]+$"
    match = _is_match(_account, pattern)
    LC = _len_check(_account)
    if match == None or not LC:
        Err = "account format error"
        return make_response(jsonify({"status": Err}), 200)
        
    #password check 英數，至少6碼至多20碼
    pattern = r"[a-zA-Z0-9]+$"
    DP = _different_password(_password, _confirm_password)
    LC = _len_check(_password)
    match = _is_match(_password, pattern)
    if not DP or not LC or match == None:
        Err = "password format error"
        return make_response(jsonify({"status": Err}), 200)
    
    #e-mail check
    req = MODEL.get({"e-mail":_email})
    if req != None:
        Err = "email already exists"
        return make_response(jsonify({"status": Err}), 200)
    pattern = r"^\w+((-\w+)|(\.\w+))*\@[A-Za-z0-9]+((\.|-)[A-Za-z0-9]+)*\.[A-Za-z]+$"
    match = _is_match(_email, pattern)
    if match == None:
        Err = "E-mail format error"
        return make_response(jsonify({"status": Err}), 200)

    #phone check
    pattern = r"^09\d{8}$"
    match = _is_match(_phone, pattern)
    if match == None:
        Err = "phone format error"
        return make_response(jsonify({"status": Err}), 200)

    #make json
    new_user = {
        "account_avator": None,
        "first_name": _First_name,
        "last_name":  _Last_name,
        "nick_name": _Nick_name,
        "account": _account,
        "password": _password,
        "e-mail": _email,
        "phone": _phone,
        "birth_date": None,
        "sex": None,
        "market_discription": None,
        "browsing_history": None,
        "cart": None,
        "notifications": None,
        "star": None,
        "knockroom": None
    }

    req = MODEL.new(new_user)
    return make_response(jsonify({"status": "ok"}), 200)
