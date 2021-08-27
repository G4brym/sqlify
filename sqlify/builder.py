# -*- coding: utf-8 -*-
from collections import namedtuple
from datetime import datetime
from io import StringIO
from logging import Logger
from typing import Optional, List, Tuple, Union, Dict, IO, Iterable

from .operators import RawSQL, IncreaseSQL, DecreaseSQL, SqlOperator
from .value_objects import Order, Fetch


class BaseSqlify(object):
    connection = None
    logger = None

    def __init__(self, cursor, logger: Logger = None):
        self._cursor = cursor
        self._logger = logger

    @property
    def _database_parameter_format(self):
        raise NotImplementedError("Database parameter not defined")

    def _format_parameter(self, parameter: str) -> str:
        raise NotImplementedError("Database parameter not defined")

    def _format_where(self, where: Optional[Union[Tuple[Union[List, str], Union[List, Dict]], Union[List, str]]]) \
            -> Optional[Tuple[str, Union[List, Dict]]]:
        if where and len(where) > 0 and isinstance(where[0], list):
            # Where is a list, we must convert it into a string
            where = (" and ".join(where[0]), where[1])

        return where

    def fetchone(
            self,
            table: str,
            fields: Optional[Union[str, List[str]]] = "*",
            where: Optional[Tuple[Union[List, str], Union[List, Dict]]] = None,
            order: Optional[Tuple[str, Union[Order, str]]] = None,
            offset: int = None,
    ) -> Optional[Dict]:
        """Get a single result
        table = (str) table_name
        fields = (field1, field2 ...) list of fields to select
        where = ("parameterized_statement", [parameters])
                eg: ("id=%s and name=%s", [1, "test"])
        order = [field, ASC|DESC]
        """
        where = self._format_where(where)
        cur = self._select(table, fields, where, order, 1, offset)
        return cur.fetchone()

    def fetchall(
            self,
            table: str,
            fields: Optional[Union[str, List[str]]] = "*",
            where: Optional[Tuple[Union[List, str], Union[List, Dict]]] = None,
            order: Optional[Tuple[str, Order]] = None,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
    ) -> Optional[List[Dict]]:
        """Get all results
        table = (str) table_name
        fields = (field1, field2 ...) list of fields to select
        where = ("parameterized_statement", [parameters])
                eg: ("id=%s and name=%s", [1, "test"])
        order = [field, ASC|DESC]
        limit = [limit, offset]
        """
        where = self._format_where(where)
        cur = self._select(table, fields, where, order, limit, offset)
        return cur.fetchall()

    def join(
            self,
            tables=(),
            fields=(),
            join_fields=(),
            where=None,
            order=None,
            limit=None,
            offset=None,
    ):
        """Run an inner left join query
        tables = (table1, table2)
        fields = ([fields from table1], [fields from table 2])  # fields to select
        join_fields = (field1, field2)  # fields to join. field1 belongs to table1 and field2 belongs to table 2
        where = ("parameterized_statement", [parameters])
                eg: ("id=%s and name=%s", [1, "test"])
        order = [field, ASC|DESC]
        limit = [limit1, limit2]
        """
        where = self._format_where(where)
        cur = self._join(tables, fields, join_fields, where, order, limit, offset)
        result = cur.fetchall()

        rows = None
        if result:
            Row = namedtuple("Row", [f[0] for f in cur.description])
            rows = [Row(*r) for r in result]

        return rows

    def insert(
            self,
            table: str,
            data: Dict[str, Union[str, bool, int, datetime]],
            returning: str = None,
    ) -> Optional[Dict]:
        """Insert a record"""
        cols, vals = self._format_insert(data)
        sql = "INSERT INTO {} ({}) VALUES({})".format(table, cols, vals)
        sql += self._returning(returning)
        cur = self.execute(sql, list(data.values()))
        return cur.fetchone() if returning else cur.rowcount

    def update(
            self,
            table: str,
            data: Dict[str, Union[str, bool, int, datetime, SqlOperator]],
            where: Optional[Tuple[Union[List, str], Union[List, Dict]]] = None,
            returning: str = None,
    ) -> Optional[Dict]:
        """Insert a record"""
        where = self._format_where(where)
        query = self._format_update(data)
        arguments = {}
        for key, value in data.items():
            arguments[key + "_datainput"] = value

        sql = "UPDATE {} SET {}".format(table, query)
        sql += self._where(where) + self._returning(returning)

        if where and len(where) > 1 and where[1]:
            arguments.update(where[1])

        cur = self.execute(sql, arguments)
        return cur.fetchall() if returning else cur.rowcount

    def delete(
            self,
            table: str,
            where: Optional[Tuple[Union[List, str], Union[List, Dict]]] = None,
            returning: str = None,
    ) -> Optional[Dict]:
        """Delete rows based on a where condition"""
        where = self._format_where(where)
        sql = f"DELETE FROM {table}"
        sql += self._where(where) + self._returning(returning)
        cur = self.execute(sql, where[1] if where and len(where) > 1 else None)
        return cur.fetchall() if returning else cur.rowcount

    def execute(
            self,
            sql,
            params=None,
            fetch: Optional[Fetch] = None,
    ) -> Union[None, Iterable, Dict]:
        """Executes a raw query"""
        # self._cursor.timestamp = time.time()
        self._cursor.execute(sql, params or ())
        # self._logger.debug("query", self._cursor.query)

        return self._cursor

    def copy_expert(
            self,
            file: Union[IO, StringIO],
            table: str,
            fields: Optional[Union[str, List[str]]] = "*",
            where: Optional[Tuple[Union[List, str], Union[List, Dict]]] = None,
            order: Optional[Tuple[str, Order]] = None,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
    ) -> IO:
        """Export query to file
        table = (str) table_name
        fields = (field1, field2 ...) list of fields to select
        where = ("parameterized_statement", [parameters])
                eg: ("id=%s and name=%s", [1, "test"])
        order = [field, ASC|DESC]
        limit = [limit, offset]
        """
        where = self._format_where(where)
        sql = self._format_select(table, fields, where, order, limit, offset)
        sql = f"copy ({sql}) to stdout with csv delimiter ',' header"
        sql = self._cursor.mogrify(sql, where[1] if where and len(where) > 1 else None)

        return self._cursor.copy_expert(sql=sql, file=file)

    def truncate(self, table: str, restart_identity: bool = False, cascade: bool = False) -> None:
        """Truncate a table or set of tables
        db.truncate('tbl1')
        db.truncate('tbl1, tbl2')
        """
        sql = f"TRUNCATE {table}"
        if restart_identity:
            sql += " RESTART IDENTITY"
        if cascade:
            sql += " CASCADE"
        self.execute(sql)

    def drop(self, table: str, cascade: bool = False) -> None:
        """Drop a table"""
        sql = f"DROP TABLE IF EXISTS {table}"
        if cascade:
            sql += " CASCADE"
        self.execute(sql)

    def create(self, table: str, schema: str) -> None:
        """Create a table with the schema provided
        pg_db.create('my_table','id SERIAL PRIMARY KEY, name TEXT')"""
        self.execute("CREATE TABLE {} ({})".format(table, schema))

    def commit(self) -> None:
        """Commit a transaction"""
        self._cursor.connection.commit()

    def rollback(self) -> None:
        """Roll-back a transaction"""
        self._cursor.connection.rollback()

    def _format_insert(self, data):
        """Format insert dict values into strings"""
        cols = ",".join(data.keys())
        vals = ",".join([self._database_parameter_format for k in data])

        return cols, vals

    def _format_update(self, data):
        """Format update dict values into string"""
        arguments = []
        for key, value in data.items():
            if isinstance(value, RawSQL):
                arguments.append(f"{key} = {value}")
            elif isinstance(value, IncreaseSQL):
                arguments.append(f"{key} = {key} + {self._format_parameter(key + '_datainput')}")
            elif isinstance(value, DecreaseSQL):
                arguments.append(f"{key} = {key} - {self._format_parameter(key + '_datainput')}")
            else:
                arguments.append(f"{key} = {self._format_parameter(key + '_datainput')}")
        return ",".join(arguments)  # This removed the last comma in string

    def _where(self, where=None):
        if where and len(where) > 0 and where[0]:
            return " WHERE %s" % where[0]
        return ""

    def _order(self, order=None):
        sql = ""
        if order:
            sql += " ORDER BY %s" % order[0]

            if len(order) > 1:
                sql += " %s" % (order[1].value if isinstance(order[1], Order) else order[1])
        return sql

    def _limit(self, limit):
        if limit:
            return " LIMIT %d" % limit
        return ""

    def _offset(self, offset):
        if offset:
            return " OFFSET %d" % offset
        return ""

    def _returning(self, returning):
        if returning:
            return " RETURNING %s" % returning
        return ""

    def _format_select(
            self, table=None, fields=(), where=None, order=None, limit=None, offset=None
    ):
        if isinstance(fields, str):
            fields = [fields]  # TODO: move this out of here

        return (
                "SELECT {} FROM {}".format(",".join(fields), table)
                + self._where(where)
                + self._order(order)
                + self._limit(limit)
                + self._offset(offset)
        )

    def _select(
            self, table=None, fields=(), where=None, order=None, limit=None, offset=None
    ):
        """Run a select query"""
        sql = self._format_select(
            table=table,
            fields=fields,
            where=where,
            order=order,
            limit=limit,
            offset=offset,
        )
        return self.execute(sql, where[1] if where and len(where) == 2 else None)

    def _join(
            self,
            tables=(),
            fields=(),
            join_fields=(),
            where=None,
            order=None,
            limit=None,
            offset=None,
    ):
        """Run an inner left join query"""

        fields = [tables[0] + "." + f for f in fields[0]] + [
            tables[1] + "." + f for f in fields[1]
        ]

        sql = "SELECT {:s} FROM {:s} LEFT JOIN {:s} ON ({:s} = {:s})".format(
            ",".join(fields),
            tables[0],
            tables[1],
            "{}.{}".format(tables[0], join_fields[0]),
            "{}.{}".format(tables[1], join_fields[1]),
        )

        sql += (
                self._where(where)
                + self._order(order)
                + self._limit(limit)
                + self._offset(offset)
        )

        return self.execute(sql, where[1] if where and len(where) > 1 else None)

    def __del__(self):
        try:
            self._cursor.close()
        except Exception as e:  # TODO: Narrow down this exception
            if "Cannot operate on a closed database." not in str(e):
                raise e


class Psycopg2Sqlify(BaseSqlify):
    _database_parameter_format = "%s"

    def _format_parameter(self, parameter: str) -> str:
        return f"%({parameter})s"


class Sqlite3Sqlify(BaseSqlify):
    _database_parameter_format = "?"

    def _format_parameter(self, parameter: str) -> str:
        return f":{parameter}"
