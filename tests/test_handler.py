
import unittest
import logging

from pymongo.connection import Connection

from mongolog.handlers import MongoHandler

class TestHandler(unittest.TestCase):

    def setUp(self):
        """ Create an empty database that could be used for logging """
        self.db_name = '_mongolog_test'

        self.conn = Connection('localhost')
        self.conn.drop_database(self.db_name)

        self.db = self.conn[self.db_name]
        self.collection = self.db['log']

    def tearDown(self):
        """ Drop used database """
        self.conn.drop_database(self.db_name)


    def testLogging(self):
        """ Simple logging example """
        log = logging.getLogger('example')
        log.setLevel(logging.DEBUG)

        log.addHandler(MongoHandler(self.collection))

        log.debug('test')

        r = self.collection.find_one({'level':'debug', 'msg':'test'})
        self.assertEquals(r['msg'], 'test')

    def testLoggingException(self):
        """ Logging example with exception """
        log = logging.getLogger('example')
        log.setLevel(logging.DEBUG)

        log.addHandler(MongoHandler(self.collection))

        try:
            1/0
        except ZeroDivisionError:
            log.error('test', exc_info=True)

        r = self.collection.find_one({'level':'error'})
        assert r['msg'].startswith('test\nTraceback')
        assert r['exc_info'].startswith('Traceback')

    def testLoggingWithExtra(self):
        """ Logging example with exception """
        log = logging.getLogger('example')
        log.setLevel(logging.DEBUG)
        log.addHandler(MongoHandler(self.collection))

        log.info('extra', extra={'more':123})

        r = self.collection.find_one({'level':'info', 'msg':'extra'})
        self.assertEquals(r['extra']['more'], 123)

    def testLoggingWithExtraV2(self):
        """ Logging example with exception """
        log = logging.getLogger('example')
        log.setLevel(logging.DEBUG)
        log.addHandler(MongoHandler(self.collection))

        log.info('extra', more=123)
        r = self.collection.find_one({'level':'info', 'msg':'extra'})
        self.assertEquals(r['extra']['more'], 123)


    def testLoggingWithExtraV3(self):
        """ Logging example with exception """
        log = logging.getLogger('example')
        log.setLevel(logging.DEBUG)
        log.addHandler(MongoHandler(self.collection))

        log.info('extra', more={'moar':456})
        r = self.collection.find_one({'level':'info', 'msg':'extra'})
        self.assertEquals(r['extra']['more']['moar'], 456)


