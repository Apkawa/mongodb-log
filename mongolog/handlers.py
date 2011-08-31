# -*- coding: utf-8 -*-
import logging

from pymongo.connection import Connection
from pymongo.collection import Collection


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

        try:
            from django.db import models
            from django.db.models.query import QuerySet
            from django.utils.datastructures import MergeDict
            from django.utils.encoding import smart_str
            if isinstance(data, models.Model):
                return data.pk

            if isinstance(data, QuerySet):
                return smart_str(data)


            if isinstance(data, MergeDict):
                return dict((key, MongoFormatter.prepare_data(value))
                            for key, value in data.iteritems())
        except ImportError:
            smart_str = str

        return smart_str(data)

    def format(self, record):
        """Format exception object as a string"""
        data = record._raw.copy()

        data['extra'] = self.prepare_data(data.get('extra'))


        if 'exc_info' in data and data['exc_info']:
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

    def __init__(self, collection,
                 db='mongolog',
                 host='localhost', port=None, level=logging.NOTSET):
        """
        Init log handler and store the collection handle
        """
        logging.Handler.__init__(self, level)
        if isinstance(collection, Collection):
            self.collection = collection
        else:
            self.collection = Connection(host, port)[db][collection]
        self.formatter = MongoFormatter()


    def emit(self, record):
        """ Store the record to the collection. Async insert """
        self.collection.save(self.format(record))

