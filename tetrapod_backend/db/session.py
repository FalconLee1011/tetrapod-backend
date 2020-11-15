import pymongo
from . import connection

class session:
    def __init__(self, collection_name):
        self.collection_name = collection_name
        self.collection = connection.getDB().get_collection(collection_name)

    def get_collection(self):
        return self.collection