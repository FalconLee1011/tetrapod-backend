from .lib import config, log
from .db import connection
import logging

CONF = None
MONGO = None

_LOGGER = logging.getLogger()

def init():
    global CONF, MONGO
    log.init()
    CONF = config.loadConfig("config/config.yaml")
    MONGO = connection.connect(CONF.get("db"))

def run_app():
    global CONF
    # * THIS IS BADDDDD SOOOO FUCKING BADDDDD, BUT I AM JUST 2 LAZY 2 MAKE IT LEGIT
    _LOGGER.info("[init] Registering APIs by a nasty way...")
    # * Following shit code is reserved for legacy method
    # from .app.legacy import app, testAPI, login, register, edit_account, upload_merchant, delete_merchant, logout, reset_password
    # * The new API regisger method is replaced by another shit way though.
    from .app import app, auth, knock, merchant, tracking, files, notification, socketService, accounts, order

    app_host = CONF.get("app", {}).get("host", "127.0.0.1")
    app_port = CONF.get("app", {}).get("port", 9000)
    app.app.config.update(
        MAIL_SERVER='smtp.gmail.com',
        MAIL_PORT=587,
        MAIL_USE_TLS=True,
        MAIL_USERNAME=CONF.get("app", {}).get("mail_account"),
        MAIL_PASSWORD=CONF.get("app", {}).get("mail_pass")
    )
    _LOGGER.info("[init] Mail")
    app.init_mail()
    app.app.run(host=app_host, port=app_port)

if __name__ == "__main__":
    init()
    run_app()
    # print(CONF)