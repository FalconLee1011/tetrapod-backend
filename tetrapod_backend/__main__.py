from .lib import config, log
from .db import connection
import logging

CONF = None
MONGO = None
DEPLOY_APP = None

_LOGGER = logging.getLogger()

def init():
    global CONF, MONGO
    log.init()
    CONF = config.loadConfig("config/config.yaml")
    MONGO = connection.connect(CONF.get("db"))

def init_app():
    global CONF, DEPLOY_APP
    # * THIS IS BADDDDD SOOOO FUCKING BADDDDD, BUT I AM JUST 2 LAZY 2 MAKE IT LEGIT
    _LOGGER.info("[init] Registering APIs by a nasty way...")
    # * Following shit code is reserved for legacy method
    # from .app.legacy import app, testAPI, login, register, edit_account, upload_merchant, delete_merchant, logout, reset_password
    # * The new API regisger method is replaced by another shit way though.
    from .app import app, auth, knock, merchant, tracking, files, notification, socketService, accounts, order

    app.app.config.update(
        MAIL_SERVER='smtp.gmail.com',
        MAIL_PORT=587,
        MAIL_USE_TLS=True,
        MAIL_USERNAME=CONF.get("app", {}).get("mail_account"),
        MAIL_PASSWORD=CONF.get("app", {}).get("mail_pass")
    )
    _LOGGER.info("[init] Mail")
    app.init_mail()
    DEPLOY_APP = app.app
    _LOGGER.info("[init] App has been initialized.")

init()
init_app()

def main():
    global DEPLOY_APP
    app_host = CONF.get("app", {}).get("host", "127.0.0.1")
    app_port = CONF.get("app", {}).get("port", 9000)
    multi_threaded = CONF.get("app", {}).get("multi_threaded", False)
    
    DEPLOY_APP.run(host=app_host, port=app_port, threaded=multi_threaded)

if __name__ == "__main__":
    main()
    # print(CONF)