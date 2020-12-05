from ..db.models import account, token
from .app import *
import time, re

@app.route("/editaccount",methods=["POST"])
@account.Account.validate
def _edit_account(*args,**kwargs):
    def _len_check(s):
        if len(s) > 5 and len(s) < 21:
            return True
        else:
            return False

    def _different_password(str1:str, str2:str):
        match = re.findall(str1, str2)
        if match:
            return True
        else:
            return False

    def _is_match(s, pat):
        return re.findall(pat, s)

    data = request.get_json()
    _account_avator = data.get("account_avator","")
    _First_name = data.get("first name","")
    _Last_name = data.get("last name","")
    _Nick_name = data.get("nick name","")
    _password = data.get("password","")
    _confirm_password = data.get("confirm password","")
    _email = data.get("e-mail","")
    _phone = data.get("phone","")
    _birth_date = data.get("birth date","")
    _sex = data.get("sex","")
    _token = data.get("token","")
        
    #password check 英數，至少6碼至多20碼
    pattern = "[a-zA-z0-9]*"
    DP = _different_password(_password, _confirm_password)
    LC = _len_check(_password)
    match = _is_match(_password, pattern)
    if not (DP and LC and match):
        Err = "password format error"
        return make_response(jsonify({"status": Err}), 200)
    
    #e-mail check
    pattern = r"^\w+((-\w+)|(\.\w+))*\@[A-Za-z0-9]+((\.|-)[A-Za-z0-9]+)*\.[A-Za-z]+$"
    match = _is_match(_email, pattern)
    if not match:
        Err = "E-mail format error"
        return make_response(jsonify({"status": Err}), 200)

    #phone check
    pattern = r"^09\d{8}$"
    match = _is_match(_phone, pattern)
    if not match:
        Err = "phone format error"
        return make_response(jsonify({"status": Err}), 200)

    #make json
    user = {
        "account_avator": _account_avator,
        "first_name": _First_name,
        "last_name":  _Last_name,
        "nick_name": _Nick_name,
        "password": _password,
        "e-mail": _email,
        "phone": _phone,
        "birth_date": _birth_date,
        "sex": _sex
    }
    account_MODEL = account.Account()
    account_req = account_MODEL.update({"account":kwargs["account"]},{"$set":user})
    return make_response(jsonify("edit account success"),200)