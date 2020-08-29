from pymongo import MongoClient
from bson.objectid import ObjectId
import syslog
from flask import current_app

class MongoDriver(object):
    def __init__(self, ip='localhost', port=27017):
        """Init MongoDB Option.
            wait more option added.
        """
        self.ip = ip
        self.port = port

    def init_connect(self):
        """ Connect To MongoDB.
            return True or False.
        """
        try:
            self.client = MongoClient(self.ip, self.port)
        except Exception as e:
            current_app.logger
            syslog.syslog(syslog.LOG_ERR, "MongoClient Connect failed :  " + str(e))
            return False
        else:
            return True

    def init_db(self, db):
        """ Connect To MongoDB -> DB.
            return True or False.
        """
        try:
            self.db = self.client[db]
        except Exception as e:
            syslog.syslog(syslog.LOG_ERR, "MongoClient Getdb {db} failed:".format(db=db) + str(e))
            self.db = ""
            return False
        else:
            return True

    def init_collection(self, collection):
        """ Connect To MongoDB -> DB -> collection.
            return True or False.
        """

        try:
            self.collection = self.db[collection]
        except Exception as e:
            syslog.syslog(syslog.LOG_ERR,\
                "MongoClient GetCollection {collection} failed:".format(collection=collection) + str(e))
            self.collection = ""
            return False
        else:
            return True
    def format_id(self, object_id):
        """
            Format Id.
            return a dict.
        """
        return {'_id': ObjectId(object_id)}

    def insert_one(self, document):
        """
            Insert One Document To MongoDB.
            document must be a dict.
            return a dict with document's inserted_id or False when Error occured
        """
        if not isinstance(document, dict):
            raise TypeError
        try:
            return self.collection.insert_one(document).inserted_id
        except Exception as e:
            syslog.syslog(syslog.LOG_ERR,\
                "MongoClient Insert_one {document} failed:".format(document=document) + str(e))
            return False

    def insert_many(self, documents):
        """
            Insert Many Documents To MongoDB.
            documents must be a list.
            eveny document must be a dict.
            return a list with documents's inserted_ids or False when Error occured
        """
        if not isinstance(documents, list):
            raise TypeError
        for document in documents:
            if not isinstance(document, dict):
                raise TypeError
        try:
            return self.collection.insert_many(documents).inserted_ids
        except Exception as e:
            syslog.syslog(syslog.LOG_ERR,\
                "MongoClient insert_many {document} failed:".format(document=document) + str(e))
            return False

    def find_one_by_id(self, object_id):
        """
            Find Result By Object_id.
            Return a dict with a document
        """
        if not isinstance(object_id, str):
            raise TypeError
        try:
            return self.collection.find_one(self.format_id(object_id))

        except Exception as e:
            syslog.syslog(syslog.LOG_ERR,\
                "MongoClient find_by_id {id} failed:".format(id=object_id) + str(e))
            return False

    def find_one_by_param(self, kws):
        """
            Find Document By Object_id.
            return a dict with a document
        """
        if not isinstance(kws, dict):
            raise TypeError
        try:
            return self.collection.find_one(kws)
        except Exception as e:
            syslog.syslog(syslog.LOG_ERR,\
                "MongoClient find_by_param {kws} failed:".format(kws=kws) + str(e))
            return False

    def find_many_by_param(self, kws):
        """
            Find Document By Object_id.
            return a cursor object with a or many document
        """
        if not isinstance(kws, dict):
            raise TypeError
        try:
            return self.collection.find(kws)
        except Exception as e:
            syslog.syslog(syslog.LOG_ERR,\
                "MongoClient find_by_param {kws} failed:".format(kws=kws) + str(e))
            return False

    def update_one_by_id(self, object_id, kws):
        """
            Update Document By Object_id.
            Return True or False
        """
        if not isinstance(kws, dict) :
            raise TypeError

        try:
            self.collection.update_one(self.format_id(object_id), {"$set": kws}, upsert=False)
        except Exception as e:
            syslog.syslog(syslog.LOG_ERR,\
                "MongoClient update_one_by_id failed:" + str(e))
            return False
        else:
            return True
    def update_one_by_param(self, condition, kws):
        """
            Update Document By Object_id.
            Return True or False
        """
        if not isinstance(condition, dict) or not isinstance(kws, dict):
            raise TypeError
        try:
            self.collection.update_one(condition, {"$set": kws}, upsert=False)
        except Exception as e:
            syslog.syslog(syslog.LOG_ERR,\
                "MongoClient update_one_by_param  failed:" + str(e))
            return False
        else:
            return True

    def update_many_by_param(self, condition, kws):
        """
            Update Document By Object_id.
            Return True or False
        """
        if not isinstance(condition, dict) or not isinstance(kws, dict):
            raise TypeError
        try:
            self.collection.update_many(condition, {"$set": kws}, upsert=False)
        except Exception as e:
            syslog.syslog(syslog.LOG_ERR,\
                "MongoClient update_many_by_param  failed:" + str(e))
            return False
        else:
            return True

    def remove_all(self):
        """
            Remove all documents from a collection .
            Return True or False
        """
        try:
            self.collection.remove()
        except Exception as e:
            syslog.syslog(syslog.LOG_ERR,\
                "MongoClient remove_all  failed:" + str(e))
            return False
        else:
            return True

    def remove_documents(self, kws):
        """
            Remove some documents from a collection .
            Return True or False
        """
        if not isinstance(kws, dict):
            raise TypeError
        try:
            self.collection.remove(kws)
        except Exception as e:
            syslog.syslog(syslog.LOG_ERR,\
                "MongoClient remove_documents  failed:" + str(e))
            return False
        else:
            return True