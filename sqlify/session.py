# -*- coding: utf-8 -*-
from typing import Optional, Union, Any, Type

from .builder import BaseSqlify, Psycopg2Sqlify, Sqlite3Sqlify
from .value_objects import DatabaseType

try:
    from psycopg2._psycopg import connection as psycopg2_connection
except ModuleNotFoundError:
    psycopg2_connection = None

try:
    from sqlite3 import Connection as sqlite3_connection, ProgrammingError
except ModuleNotFoundError:
    sqlite3_connection = None


class Session(object):
    _database_type: DatabaseType
    _manager: Type[BaseSqlify]

    def __init__(self, connection: Union[psycopg2_connection, sqlite3_connection],
                 database_type: Optional[DatabaseType] = None, autocommit: Optional[bool] = True):
        self._connection = connection
        self._autocommit = autocommit

        if database_type is not None:
            self._database_type = database_type
        elif psycopg2_connection and isinstance(self._connection, psycopg2_connection):
            self._database_type = DatabaseType.PSYCOPG2
            self._manager = Psycopg2Sqlify
        elif sqlite3_connection and isinstance(self._connection, sqlite3_connection):
            self._database_type = DatabaseType.SQLITE3
            self._manager = Sqlite3Sqlify
        else:
            raise RuntimeError(
                "Could not detect the correct database type, please supply the 'database_type' parameter")

        self.session = self._manager(self.get_cursor())

    @property
    def is_open(self) -> bool:
        if self._database_type == DatabaseType.PSYCOPG2:
            return not self._connection.closed
        elif self._database_type == DatabaseType.SQLITE3:
            return True
        raise NotImplementedError("Database type not implemented")

    def close(self) -> None:
        self._connection.close()

    def get_cursor(self) -> Any:
        return self._connection.cursor()

    def __enter__(self):
        return self.session

    def __exit__(self, type_, value, traceback):
        if self._autocommit:
            if isinstance(type_, Exception):
                self._connection.rollback()
            else:
                self._connection.commit()

        if self.is_open:
            self.close()
