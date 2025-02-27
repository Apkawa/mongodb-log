
import logging
import sys
import os

from socket import gethostname
from datetime import datetime

__all__ = ['MongoLogRecord', 'MongoLogger']


class MongoLogRecord(logging.LogRecord):
    def __init__(self, name, level, fn, lno,
                 msg, args, exc_info, func, extra=None):

        logging.LogRecord.__init__(self, name, level, fn, lno,
                                   msg, args, exc_info, func)

        self.username = _current_user()
        self.funcname = _calling_func_name()

        self._raw = {
            'name': name,
            'level': _level_to_str(level),
            'levelno': level,
            'file': fn,
            'line_no': lno,
            'msg': msg,
            'args': list(args),
            'exc_info': exc_info,
            'user': self.username,
            'funcname': self.funcname,
            'time': datetime.now(),
            'host': gethostname(),
            'extra': extra,
        }


_LoggerClass = logging.getLoggerClass()
class MongoLogger(_LoggerClass):
    def makeRecord(self, *args, **kwargs):
        return MongoLogRecord(*args, **kwargs)

    def _log(self, level, msg, args, **kwargs):
        exc_info = kwargs.get('exc_info')
        extra = kwargs.get('extra', {})

        if 'extra' in kwargs:
            del kwargs['extra']
        if 'exc_info' in kwargs:
            del kwargs['exc_info']

        extra.update(kwargs)
        _LoggerClass._log(self, level, msg, args, exc_info, extra)


def _level_to_str(level):
    """ Convert a numeric logging level to string representation  """
    if logging.DEBUG == level:
        return u'debug'
    elif logging.INFO == level:
        return u'info'
    elif logging.WARNING == level:
        return u'warning'
    elif logging.ERROR == level:
        return u'error'
    elif logging.CRITICAL == level:
        return u'critical'
    else:
        return u'undefined'


def _current_user():
    """ Get the name of the os user running this app """
    try:
        import pwd
    except ImportError:
        return "(unknown<win32>)"
    import os
    try:
        return pwd.getpwuid(os.getuid()).pw_name
    except KeyError:
        return "(unknown)"


def _calling_func_name():
    return _calling_frame().f_code.co_name


def _calling_frame():
    f = sys._getframe()

    while True:
        if _is_user_source_file(f.f_code.co_filename):
            return f
        f = f.f_back


def _is_user_source_file(filename):
    return os.path.normcase(filename) not in (_srcfile, logging._srcfile)


def _current_source_file():
    if __file__[-4:].lower() in ['.pyc', '.pyo']:
        return __file__[:-4] + '.py'
    else:
        return __file__


_srcfile = os.path.normcase(_current_source_file())
