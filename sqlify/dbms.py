import abc
import logging
from sqlite3 import connect as sqlite3_connect

from .builder import Sqlify

try:
    from psycopg2 import connect as postgresql_connect
except ModuleNotFoundError:
    postgresql_connect = None


class DBMS(abc.ABC):
    def __init__(self, *args, **kwargs):
        self.logger = kwargs.pop("logger", logging.getLogger('sqlify'))

        self.args = args
        self.kwargs = kwargs

    @abc.abstractmethod
    def get_conn(self):
        pass

    @property
    def atomic(self):
        return Sqlify(self.get_conn(), self.logger)


class SqliteDatabase(DBMS):
    def get_conn(self):
        return sqlite3_connect(*self.args, **self.kwargs)


class PostgresqlDatabase(DBMS):
    def get_conn(self):
        return postgresql_connect(*self.args, **self.kwargs)
