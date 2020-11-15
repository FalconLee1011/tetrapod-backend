import yaml

CONF = None

def loadConfig(path):
    global CONF
    with open(path) as f:
        CONF =  yaml.load(f, Loader=yaml.SafeLoader)
        f.close()
    return CONF

def loadConfigAndReturnAsLocalVariable(path):
    with open(path) as f:
        conf_let =  yaml.load(f, Loader=yaml.FullLoader)
        f.close()
    return conf_let

def getConfig():
    return CONF