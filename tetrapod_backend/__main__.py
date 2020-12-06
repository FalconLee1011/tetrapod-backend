from .lib import config, log
from .app import app
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
    # THIS IS BADDDDD SOOOO FUCKING BADDDDD, BUT I AM JUST 2 LAZY 2 MAKE IT LEGIT
    
    _LOGGER.info("[init] Registering APIs by a nasty way...")
    from .app import app, testAPI, login, register, edit_account, upload_merchant, delete_merchant
    app_host = CONF.get("app", {}).get("host", "127.0.0.1")
    app_port = CONF.get("app", {}).get("port", 9000)
    app.app.run(host=app_host, port=app_port)

if __name__ == "__main__":
    init()
    run_app()
    # print(CONF)