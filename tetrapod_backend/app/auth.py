from ..db.models import account, token, verification
from .app import *
from ..lib import config
import re, jwt, random, string, logging
from time import time
from flask_mail import Message
from ..lib.config import getConfig
from threading import Thread

from ._fileHandler import _fileHandler

_LOGGER = logging.getLogger()

MODULE_PREFIX = '/auth'
FILE_HANDLER = _fileHandler()
account_MODEL = account.Account()
token_MODEL = token.Token()
verification_MODEL = verification.Verification()

def _len_check(s):
    if len(s) > 5 and len(s) < 21:
        return True
    return False

def _different_password(str1, str2):
    if str1 == str2:
        return True
    return False

def _is_match(s, pat):
    return re.findall(pat, s)

def send_async_email(app, msg):
    with app.app_context():
        get_mail().send(msg)

def _tokenGenerator(N):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))

def check_email(_email):
    pattern = r"^\w+((-\w+)|(\.\w+))*\@[A-Za-z0-9]+((\.|-)[A-Za-z0-9]+)*\.[A-Za-z]+$"
    match = re.findall(pattern, _email)
    return match

@app.route(f"{MODULE_PREFIX}/editaccount",methods=["POST"])
@account.Account.validate
def _edit_account(*args,**kwargs):    
    data = request.form
    _account_avator = ""
    try: _account_avator = FILE_HANDLER.save(files=request.files.getlist("account_avator[]"))[0]
    except: _LOGGER.warning("NO PHOTO")
    # _LOGGER.debug(f"\033[38;5;10m PHOTO -------> {_account_avator}")
    # return make_response(jsonify({"photos": _account_avator}), 503)
    _First_name = data.get("first_name","")
    _Last_name = data.get("last_name","")
    _Nick_name = data.get("nick_name","")
    _password = data.get("password","")
    _confirm_password = data.get("confirm_password","")
    _email = data.get("e-mail","")
    _phone = data.get("phone","")
    _birth_date = data.get("birth_date","")
    _sex = data.get("sex","")
    _description = data.get("market_description","")
        
    #password check 英數，至少6碼至多20碼
    # pattern = r"[a-zA-Z0-9]+$"
    # DP = _different_password(_password, _confirm_password)
    # LC = _len_check(_password)
    # match = _is_match(_password, pattern)
    # if not (DP and LC and match):
        # Err = "password format error"
        # return make_response(jsonify({"status": Err}), 200)
    
    #e-mail check
    req = account_MODEL.get({"e-mail":_email})
    if req != None and req.get("account") != kwargs['account']:
        Err = "e-mail already exists"
        return make_response(jsonify({"status": Err}), 200)
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
        "sex": _sex,
        "market_description": _description
    }
    account_req = account_MODEL.update({"account":kwargs["account"]},{"$set":user})
    return make_response(jsonify("edit account success"),200)

@app.route(f"{MODULE_PREFIX}/register",methods=["POST"])
def _register():

    data = request.get_json()   
    _First_name = data.get("first_name","")
    _Last_name = data.get("last_name","")
    _Nick_name = data.get("nick_name","")
    _account = data.get("account","")
    _password = data.get("password","")
    # _confirm_password = data.get("confirm password","")
    _confirm_password = _password
    _email = data.get("email","")
    _phone = data.get("phone","")
    _sex = data.get("sex","")
    
    #account check 英文大小寫開頭+英數，至少6碼至多20碼
    req = account_MODEL.get({"account":_account})
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
    req = account_MODEL.get({"e-mail":_email})
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
        "account_avator": "None",
        "first_name": _First_name,
        "last_name":  _Last_name,
        "nick_name": _Nick_name,
        "account": _account,
        "password": _password,
        "e-mail": _email,
        "phone": _phone,
        "birth_date": "None",
        "sex": _sex,
        "market_description": "None",
        "browsing_history": [],
        "cart": [],
        "notifications": [],
        "star": {"star": 0, "count": 0},
        "knockroom": []
    }

    req = account_MODEL.new(new_user)
    return make_response(jsonify({"status": "ok"}), 200)

@app.route(f"{MODULE_PREFIX}/login",methods=["POST"])
def _login():
    _account = request.get_json().get("account",None)
    _password = request.get_json().get("password",None)
    account_req = account_MODEL.get({"account":_account})
    if account_req != None and _account == account_req['account'] and _password == account_req['password']:
        token_req = token_MODEL.get({"account":_account})
        secret = config.getConfig().get("app",{}).get("secret")
        # account_token = bytes.decode(jwt.encode({"account":_account,"timestamp":str(time())},secret))
        account_token = jwt.encode({"account":_account,"timestamp":str(time())},secret)
        if token_req == None:
            token_MODEL.new({"account":_account,"token":account_token})
        else:    
            token_MODEL.update({"account":_account},{"$set": {"token": account_token}})
        account_req.update({"password": None, "_id": None})
        return make_response(jsonify({"account":account_req, "token":account_token}),200)
    return make_response(jsonify("login failure"), 401)

@app.route(f"{MODULE_PREFIX}/logout",methods=["POST"])
@account.Account.validate
def _logout(*args, **kwargs):
    token_MODEL.update({"account":kwargs["account"]},{"$set":{"token":None}})
    return make_response(jsonify({"status":"ok"}),200)

@app.route(f"{MODULE_PREFIX}/validate",methods=["POST"])
def _validate(*args, **kwargs):
    front_token = request.get_json().get('token',None)
    db_token = token_MODEL.get({"token":front_token})
    secret = config.getConfig().get("app",{}).get("secret")
    _LOGGER.info("[info] validating token... (from validate API)")
    if db_token != None and front_token != None and front_token != '' and front_token == db_token.get('token'):
        _LOGGER.info("Front token: "+front_token)
        _LOGGER.info("DB token: "+db_token.get('token'))
        try:
            _LOGGER.info("[info] validate passed (from validate API)")
            return make_response({"result": True}, 200)
        except Exception as err:
            _LOGGER.error("[error] validate error (from validate API)")
            _LOGGER.error(err)
            return make_response({"result": False}, 200)
    return make_response({"result": False}, 200)

@app.route(f'{MODULE_PREFIX}/checkemail', methods=["POST"])
def _check_email():
    _email = request.get_json().get("email",None)
    _LOGGER.debug(_email)
    if not (_email and check_email(_email)):
        return make_response(jsonify("E-mail format error"),200)
    account_req = account_MODEL.get({"e-mail":_email})
    if account_req is not None and account_req["e-mail"] == _email:
        _verification_code = _tokenGenerator(6)
        msg = Message(
            '[TetrapodShop] Please verify your device!',
            sender=getConfig().get("app",{}).get("mail_account"),
            recipients=[_email],
            body=
            "Hey "+ account_req["account"]+"!\nTo complete the password reset, please enter the verification code on the device.\n\n\tVerification code: "+_verification_code+"\n\nThanks,\nThe TetrapodShop Team"
        )
        thr = Thread(target=send_async_email, args=[app, msg])
        _LOGGER.debug(msg)
        thr.start()
        verification_req = verification_MODEL.get({"account":account_req["account"]})
        if verification_req == None:
            verification_MODEL.new({"account":account_req["account"],"verification_code":_verification_code})
        else:
            verification_MODEL.update({"account":account_req["account"]},{"$set":{"verification_code":_verification_code}})
        return make_response(jsonify({"msg": "mail sended", "status": "ok"}),200)
    return make_response(jsonify("E-mail not exist"),401)

@app.route(f'{MODULE_PREFIX}/check_verification_code', methods=["POST"])
def _check_verification_code():
    _email = request.get_json().get("email",None)
    if not (_email and check_email(_email)):
        return make_response(jsonify("E-mail format error"),200)
    account_req = account_MODEL.get({"e-mail":_email})
    if account_req == None:
        return make_response(jsonify("E-mail not exist"),401)
    _user_verification = request.get_json().get("token",None)
    db_req = verification_MODEL.get({"account":account_req["account"]})
    if db_req == None:
        return make_response(jsonify("e-mail non exist"),401)
    _db_verification = db_req["verification_code"]
    if _db_verification == _user_verification:
        return make_response(jsonify({"status": "ok"}),200)
    return make_response(jsonify("verification code not match"),401)

@app.route(f'{MODULE_PREFIX}/resetpassword', methods=["POST"])
def _change_password():
    _email = request.get_json().get("email",None)
    if not (_email and check_email(_email)):
        return make_response(jsonify("E-mail format error"),200)
    account_req = account_MODEL.get({"e-mail":_email})
    if account_req == None:
        return make_response(jsonify("E-mail not exist"),401)
    _user_verification = request.get_json().get("token",None)
    db_req = verification_MODEL.get({"account":account_req["account"]})
    if db_req == None:
        return make_response(jsonify("e-mail non exist"),401)
    _db_verification = db_req["verification_code"]
    if _db_verification != _user_verification:
        return make_response(jsonify("verification code not match"),401)
    _password = request.get_json().get("password",None)
    _confirm_password = request.get_json().get("password",None)
    pattern = r"[a-zA-Z0-9]*"
    DP = _different_password(_password, _confirm_password)
    LC = _len_check(_password)
    match = _is_match(_password, pattern)
    if not (DP and LC and match):
        Err = "password format error"
        return make_response(jsonify({"status": Err}), 200)
    account_MODEL.update({"account":account_req["account"]},{"$set":{"password":_password}})
    verification_MODEL.delete({"account":account_req["account"]})
    return make_response(jsonify({"status":"ok"}),200)