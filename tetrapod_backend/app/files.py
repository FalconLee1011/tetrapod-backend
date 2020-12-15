from .app import *
from ..lib import config
from ._fileHandler import _fileHandler
import logging

MODULE_PREFIX = '/media'
_LOGGER = logging.getLogger()
FILE_HANDLER = _fileHandler()

@app.route(f"{MODULE_PREFIX}/get", methods=["POST"])
def _get_files():
    uuid = request.get_json().get("file")
    file = FILE_HANDLER.get(uuid)
    if file != None:
        return send_file(file , attachment_filename=uuid)
    else: 
        return make_response(jsonify("Resource not found"), 404)