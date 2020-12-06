import pymongo, logging
from .session import *
from collections import namedtuple
from datetime import datetime

MongoResult = namedtuple(
    "MongoResult", {"matchedCount", "modifiedCount", "documentIds",}
)

def _timestamp(key, documents):
    if(type(documents) == dict): documents[key] = datetime.now()
    elif(type(documents) == list): 
        for i, _ in enumerate(documents): documents[i][key] = datetime.now()
    return documents

class model:
    def __init__(self, collection_name):
        self.session = session(collection_name)
        self.collection = self.session.get_collection()

    def insert_one(self, mDocument):
        mDocument = _timestamp("_created", mDocument)
        mRet = self.collection.insert_one(mDocument)
        return MongoResult(
            matchedCount=None,
            modifiedCount=None,
            documentIds=[mRet.inserted_id] if mRet.inserted_id else [],
        )

    def insert_many(self, mDocuments, ordered=True):
        mDocuments = _timestamp("_created", mDocuments)
        mRet = self.collection.insert_many(mDocuments, ordered=ordered)
        return MongoResult(
            matchedCount=None, modifiedCount=None, documentIds=mRet.inserted_ids,
        )
    
    def replace_one(self, mFilter, mDocument, upsert=False):
        mDocument = _timestamp("_replaced", mDocument)
        mRet = self.collection.replace_one(mFilter, mDocument, upsert=False)
        return MongoResult(
            matchedCount=mRet.matched_count,
            modifiedCount=mRet.modified_count,
            documentIds=[mRet.upserted_id] if upsert and mRet.upserted_id else [],
        )

    def update_one(self, mFilter, mUpdate, upsert=True):
        mUpdate = _timestamp("_updated", mUpdate)
        mRet = self.collection.update_one(mFilter, mUpdate, upsert=upsert)
        return MongoResult(
            matchedCount=mRet.matched_count,
            modifiedCount=mRet.modified_count,
            documentIds=[mRet.upserted_id] if upsert and mRet.upserted_id else [],
        )
    
    def update_many(self, mFilter, mUpdate, upsert=True):
        mUpdate = _timestamp("_updated", mUpdate)
        mRet = self.collection.update_many(mFilter, mUpdate, upsert=upsert)
        return MongoResult(
            matchedCount=mRet.matched_count,
            modifiedCount=mRet.modified_count,
            documentIds=[mRet.upserted_id] if upsert and mRet.upserted_id else [],
        )

    def delete_one(self, mFilter):
        if not mFilter:
            raise MongoException.InvalidDeleteOps(mFilter)
        mRet = self.collection.delete_one(mFilter)
        return MongoResult(
            matchedCount=mRet.deleted_count,
            modifiedCount=mRet.deleted_count,
            documentIds=[],
        )

    def delete_many(self, mFilter):
        if not mFilter:
            raise MongoException.InvalidDeleteOps(mFilter)
        mRet = self.collection.delete_many(mFilter)
        return MongoResult(
            matchedCount=mRet.deleted_count,
            modifiedCount=mRet.deleted_count,
            documentIds=[],
        )

    def aggregate(self, pipeline, cursor=False):
        c = self.collection.aggregate(pipeline)
        return [v for v in c] if not cursor else c

    def find(self, mFilter, mProject=None, mSort=None, skip=0, limit=0, cursor=False):
        c = self.collection.find(
            mFilter, projection=mProject, sort=mSort, skip=skip, limit=limit
        )
        return [v for v in c] if not cursor else c
    
    def find_one(self, mFilter, mProject=None, mSort=None, skip=0):
        return self.collection.find_one(
            mFilter, projection=mProject, sort=mSort, skip=skip
        )
    
    def find_one_and_delete(self, mFilter, mProject=None, mSort=None):
        return self.collection.find_one_and_delete(
            mFilter, projection=mProject, sort=mSort
        )

    def find_one_and_replace(
        self,
        mFilter,
        mDocument,
        mProject=None,
        mSort=None,
        upsert=False,
    ):
        mDocument = _timestamp("_updated", mDocument)
        return self.collection.find_one_and_replace(
            mFilter,
            mDocument,
            projection=mProject,
            sort=mSort,
            upsert=upsert,
        )

    def find_one_and_update(
        self,
        mFilter,
        mUpdate,
        mProject=None,
        mSort=None,
        upsert=False,
    ):
        
        return self.collection.find_one_and_update(
            mFilter,
            mUpdate,
            projection=mProject,
            sort=mSort,
            upsert=upsert,
        )
    
    def count_documents(self, mFilter, skip=0, limit=0):
        return self.collection.count_documents(mFilter, skip=skip, limit=limit)

    
    def estimated_document_count(self, **kwargs):
        return self.collection.estimated_document_count(**kwargs)
