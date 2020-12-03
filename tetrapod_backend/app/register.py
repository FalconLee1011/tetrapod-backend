from ..db.models import account
from .app import *
from ..lib import config
import time
import jwt
import re
@app.route("/register",methods=["POST"])
def _register():
    def _len_check(s):
        if len(s) <=6 or len(s) >= 20:
            return False
        else:
            return True
    def _different_password(str1, str2):
        match = re.findall(str1, str2)
        if match:
            return True
        else:
            return False

    def _is_match(s, pat):
        return re.findall(s, pat)
    data = request.get_json()
    
    _First_name = data["First name"]
    _Last_name = data["Last name"]
    _Nick_name = data["Nick name"]
    _account = data["account"]
    _password = data["password"]
    _confirm_password = data["confirm password"]
    _email = data["E-mail"]
    _phone = data["phone"]
    Pass = True
    Err = ""
    COLLECTION = "account"
    MODEL = account.Account(COLLECTION)
    req = MODEL._get({"account":_account})

    #account check 英文大小寫開頭+英數，至少6碼至多20碼
    if req != None:
        Pass = False
        Err = "account already exists"
    pattern = r"[a-zA-z]+[a-zA-z0-9]*"
    match = _is_match(_account, pattern)
    LC = _len_check(_account)
    if match and LC:
        Pass = True
    else:
        Pass = False
        Err = "account format error"
        
    #password check 英數，至少6碼至多20碼
    pattern = "[a-zA-z0-9]*"
    DP = _different_password(_password, _confirm_password)
    LC = _len_check(_password)
    match = _is_match(_account, pattern)
    if DP and LC and match:
        Pass = True
    else:
        Pass = False
        Err = "password format error"
    
    #e-mail check
    pattern = r"^\w+((-\w+)|(\.\w+))*\@[A-Za-z0-9]+((\.|-)[A-Za-z0-9]+)*\.[A-Za-z]+$"
    match = _is_match(_email, pattern)
    if match:
        Pass = True
    else:
        Pass = False
        Err = "E-mail format error"

    #phone check
    pattern = r"^09[0-9]{8}$"
    match = _is_match(_phone, pattern)
    if match:
        Pass = True
    else:
        Pass = False
        Err = "phone format error"

    #make json
    new_user = {
        "First_name": _First_name,
        "Last_name":  _Last_name,
        "account": _account,
        "Password": _password,
        "E-mail": _email,
        "phone": _phone,
    }

    req = MODEL._new(new_user)
    if Pass:
        return make_response(jsonify({"status": "ok"}),200)
    else:
        return make_response(jsonify({"status": Err}), 200)