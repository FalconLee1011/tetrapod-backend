from .lib import config, log
from .app import app, testAPI
from .db import connection

CONF = None
MONGO = None

def init():
    global CONF, MONGO
    log.init()
    CONF = config.loadConfig("config/config.yaml")
    MONGO = connection.connect(CONF.get("db"))
    
def run_app():
    global CONF
    app_host = CONF.get("app", {}).get("host", "127.0.0.1")
    app_port = CONF.get("app", {}).get("port", 9000)
    app.app.run(host=app_host, port=app_port)

if __name__ == "__main__":
    init()
    run_app()
    # print(CONF)