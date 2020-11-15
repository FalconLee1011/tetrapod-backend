from pymongo import MongoClient
import logging

# CONF = config.getConfig()

MONGO = None
_LOGGER = logging.getLogger("mongo.logger")

def connect(config, timeout=3000):
    global MONGO
    host = config.get("host")
    port = config.get("port")
    user = config.get("user")
    pwd = config.get("pass")
    db_name = config.get("db")
    conn_str = f"mongodb://{user}:{pwd}@{host}:{port}/" if(not(user == None or pwd == None) and not(user == "" or pwd == "")) else f"mongodb://{host}:{port}/"
    try:
        _LOGGER.info(f"[init] Connecting to {conn_str}")
        MONGO = MongoClient(conn_str, serverSelectionTimeoutMS=timeout)[db_name]
        _LOGGER.info("[init] Connected!")
        # MONGO.close()
        return MONGO
    except Exception as err:
        _LOGGER.critical(f"ERROR connecting to {host}:{port}")
        _LOGGER.critical("Abort action.")
        _LOGGER.critical(err)
        exit(1)
        return None

def getDB():
    global MONGO
    return MONGO
