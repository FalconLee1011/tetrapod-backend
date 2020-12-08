from .app import *
from ..db.models import account, verification
from flask_mail import Message
from threading import Thread
import re, random, string
from ..lib.config import getConfig

account_MODEL = account.Account()
verification_MODEL = verification.Verification()

def send_async_email(app, msg):
    with app.app_context():
        get_mail().send(msg)

def _tokenGenerator(N):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))

def _is_match(s, pat):
    return re.findall(pat, s)

def _len_check(s):
    if len(s) > 5 and len(s) < 21:
        return True
    return False

def check_email(_email):
    pattern = r"^\w+((-\w+)|(\.\w+))*\@[A-Za-z0-9]+((\.|-)[A-Za-z0-9]+)*\.[A-Za-z]+$"
    match = re.findall(pattern, _email)
    return match

@app.route('/checkemail', methods=["POST"])
def _check_email():
    _email = request.get_json().get("e-mail",None)
    if not check_email(_email):
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
        thr.start()
        verification_req = verification_MODEL.get({"account":account_req["account"]})
        if verification_req == None:
            verification_MODEL.new({"account":account_req["account"],"verification_code":_verification_code})
        else:
            verification_MODEL.update({"account":account_req["account"]},{"$set":{"verification_code":_verification_code}})
        return make_response(jsonify("mail sended"),200)
    return make_response(jsonify("E-mail not exist"),401)

@app.route('/check_verification_code', methods=["POST"])
def _check_verification_code():
    _email = request.get_json().get("e-mail",None)
    if not check_email(_email):
        return make_response(jsonify("E-mail format error"),200)
    account_req = account_MODEL.get({"e-mail":_email})
    if account_req == None:
        return make_response(jsonify("E-mail not exist"),401)
    _user_verification = request.get_json().get("verification code",None)
    db_req = verification_MODEL.get({"account":account_req["account"]})
    if db_req == None:
        return make_response(jsonify("e-mail non exist"),401)
    _db_verification = db_req["verification_code"]
    if _db_verification == _user_verification:
        return make_response(jsonify("verification code match"),200)
    return make_response(jsonify("verification code not match"),401)

@app.route('/resetpassword', methods=["POST"])
def _change_password():
    _email = request.get_json().get("e-mail",None)
    if not check_email(_email):
        return make_response(jsonify("E-mail format error"),200)
    account_req = account_MODEL.get({"e-mail":_email})
    if account_req == None:
        return make_response(jsonify("E-mail not exist"),401)
    _user_verification = request.get_json().get("verification code",None)
    db_req = verification_MODEL.get({"account":account_req["account"]})
    if db_req == None:
        return make_response(jsonify("e-mail non exist"),401)
    _db_verification = db_req["verification_code"]
    if _db_verification != _user_verification:
        return make_response(jsonify("verification code not match"),401)
    _password = request.get_json().get("password",None)
    _confirm_password = request.get_json().get("confirm password",None)
    pattern = "[a-zA-Z0-9]*"
    DP = _password ==  _confirm_password
    LC = _len_check(_password)
    match = _is_match(_password, pattern)
    if not (DP and LC and match):
        Err = "password format error"
        return make_response(jsonify({"status": Err}), 200)
    account_MODEL.update({"account":account_req["account"]},{"$set":{"password":_password}})
    verification_MODEL.delete({"account":account_req["account"]})
    return make_response(jsonify({"status":"ok"}),200)