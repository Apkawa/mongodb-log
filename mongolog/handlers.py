# -*- coding: utf-8 -*-
import logging

from pymongo.connection import Connection
from pymongo.collection import Collection

from pymongo.errors import AutoReconnect

try:
    from django.views.debug import ExceptionReporter
    from django.db import models
    from django.db.models.query import QuerySet
    from django.utils.datastructures import MergeDict
    from django.utils.encoding import smart_str
    DJANGO_ENABLE = True
except ImportError:
    DJANGO_ENABLE = False




class MongoFormatter(logging.Formatter):

    @staticmethod
    def prepare_data(data):
        '''
        Prepairing and normalize data for bjson encoder mongo
        '''
        if isinstance(data, (list, tuple)):
            return [MongoFormatter.prepare_data(d) for d in data]

        if isinstance(data, dict):
            return dict((key, MongoFormatter.prepare_data(value))
                        for key, value in data.iteritems())

        if isinstance(data, (int, long, float, basestring)):
            return data

        if DJANGO_ENABLE:
            if isinstance(data, models.Model):
                return data.pk

            if isinstance(data, QuerySet):
                return smart_str(data)


            if isinstance(data, MergeDict):
                return dict((key, MongoFormatter.prepare_data(value))
                            for key, value in data.iteritems())
        else:
            smart_str = str

        return smart_str(data)

    def formatException(self, exc_info):
        # TODO: Super format exception
        return logging.Formatter.formatException(self, exc_info)

    def format(self, record):
        """Format exception object as a string"""
        data = record._raw.copy()

        data['extra'] = self.prepare_data(data.get('extra'))


        if 'exc_info' in data and data['exc_info']:
            if DJANGO_ENABLE:
                er = ExceptionReporter(None, *data['exc_info'])
                data['exc_extra_info'] = self.prepare_data(er.get_traceback_frames())
            data['exc_info'] = self.formatException(data['exc_info'])

        data['msg'] = logging.Formatter.format(self, record)
        data['format'] = data['msg']
        del data['args']

        # hack for normalize unicode data for soap fault
        for key in ['exc_info', 'format']:
            if isinstance(data[key], basestring):
                try:
                    data[key] = data[key].decode("unicode_escape")
                except UnicodeEncodeError:
                    pass
        return data


class MongoHandler(logging.Handler):
    """ Custom log handler

    Logs all messages to a mongo collection. This  handler is
    designed to be used with the standard python logging mechanism.
    """

    @classmethod
    def to(cls, db, collection,
           host='localhost', port=None, level=logging.NOTSET):
        """
        Create a handler for a given
        DEPRECATED:
        """
        return cls(collection=collection, db=db, host=host, port=port, level=level)


    def get_collection(self):
        collection = getattr(self, '__collection', None)
        if not collection:
            collection = Connection(self.host, self.port)[self.db][self.collection]
            self.set_collection(collection)
        return collection

    def set_collection(self, collection):
        setattr(self, '__collection', collection)

    def update_conf_from_collection(self, collection):
        self.collection = collection.name
        self.db = collection.database.name
        self.host = collection.database.connection.host
        self.port = collection.database.connection.port

    def __init__(self, collection,
                 db='mongolog',
                 host='localhost', port=None, level=logging.NOTSET):
        """
        Init log handler and store the collection handle
        """
        logging.Handler.__init__(self, level)
        if isinstance(collection, Collection):
            self.set_collection(collection)
            self.update_conf_from_collection(collection)
        else:
            self.collection = collection
            self.db = db
            self.host = host
            self.port = port

        self.formatter = MongoFormatter()

    def emit(self, record):
        """ Store the record to the collection. Async insert """
        while True:
            try:
                self.get_collection().save(self.format(record))
                break
            except AutoReconnect:
                self.set_collection(None)

