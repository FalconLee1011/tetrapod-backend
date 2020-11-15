import logging, logging.config
from .config import loadConfigAndReturnAsLocalVariable

LOGGER = logging.getLogger()

def init():
    global LOG
    conf = loadConfigAndReturnAsLocalVariable("config/log.settings.yaml")
    # logging.basicConfig(level=config.get("level", logging.DEBUG), format=config.get("format"))
    logging.config.dictConfig(conf)
    LOGGER.info("[THIS IS A DRILL!!]info!")
    LOGGER.warning("[THIS IS A DRILL!!]warning!")
    LOGGER.error("[THIS IS A DRILL!!]error!")
    LOGGER.debug("[THIS IS A DRILL!!]debug!")
    LOGGER.critical("[THIS IS A DRILL!!]critical!")
    LOGGER.info("[init] Logging")