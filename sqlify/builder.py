# -*- coding: utf-8 -*-
from datetime import datetime
from io import StringIO
from logging import Logger
from typing import Optional, List, Tuple, Union, Dict, IO, Any

from .operators import RawSQL, IncreaseSQL, DecreaseSQL, SqlOperator
from .value_objects import Order, Fetch


class BaseSqlify(object):
    connection = None
    logger = None

    def __init__(self, cursor, logger: Logger = None):
        self._cursor = cursor
        self._logger = logger

    @property
    def _unnamed_parameter(self):
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
            where: Optional[Union[str, List[str], Tuple[Union[List[str], str], Union[List, Dict]]]] = None,
            group: Optional[Union[List[str], str]] = None,
            having: Optional[str] = None,
            order: Optional[Union[str, Tuple[str, Union[Order, str]]]] = None,
            offset: int = None,
            with_sq: Optional[Dict[str, str]] = None,
    ) -> Optional[Union[Dict, List]]:
        """Get a single result
        table = (str) table_name
        fields = (field1, field2 ...) list of fields to select
        where = ("parameterized_statement", [parameters])
                eg: ("id=%s and name=%s", [1, "test"])
        order = [field, ASC|DESC]
        """
        conditions, parameters = self._split_where(where)

        sql = self._select(
            table=table,
            fields=fields,
            where=conditions,
            group=group,
            having=having,
            order=order,
            limit=1,
            offset=offset,
            with_sq=with_sq,
        )
        cur = self.execute(sql, parameters)
        return cur.fetchone()

    def fetchall(
            self,
            table: str,
            fields: Optional[Union[str, List[str]]] = "*",
            where: Optional[Union[str, List[str], Tuple[Union[List[str], str], Union[List, Dict]]]] = None,
            group: Optional[Union[List[str], str]] = None,
            having: Optional[str] = None,
            order: Optional[Union[str, Tuple[str, Union[Order, str]]]] = None,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            with_sq: Optional[Dict[str, str]] = None,
    ) -> Optional[List[Union[Dict, List]]]:
        """Get all results
        table = (str) table_name
        fields = (field1, field2 ...) list of fields to select
        where = ("parameterized_statement", [parameters])
                eg: ("id=%s and name=%s", [1, "test"])
        order = [field, ASC|DESC]
        limit = [limit, offset]
        """
        conditions, parameters = self._split_where(where)

        sql = self._select(
            table=table,
            fields=fields,
            where=conditions,
            group=group,
            having=having,
            order=order,
            limit=limit,
            offset=offset,
            with_sq=with_sq,
        )
        cur = self.execute(sql, parameters)
        return cur.fetchall()

    def insert(
            self,
            table: str,
            data: Dict[str, Union[str, bool, int, datetime]],
            returning: str = None,
    ) -> Optional[Union[Dict, int]]:
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
            where: Optional[Union[str, List[str], Tuple[Union[List[str], str], Union[List, Dict]]]] = None,
            returning: str = None,
    ) -> Optional[Union[Dict, int]]:
        """Insert a record"""
        conditions, parameters = self._split_where(where)
        query = self._format_update(data)
        arguments = {}
        for key, value in data.items():
            arguments[key + "_datainput"] = value  # TODO

        sql = "UPDATE {} SET {}".format(table, query)
        sql += self._where(conditions) + self._returning(returning)

        if parameters is not None:
            arguments.update(parameters)

        cur = self.execute(sql, arguments)
        return cur.fetchall() if returning else cur.rowcount

    def delete(
            self,
            table: str,
            where: Optional[Tuple[Union[List, str], Union[List, Dict]]] = None,
            returning: str = None,
    ) -> Optional[Union[Dict, int]]:
        """Delete rows based on a where condition"""
        conditions, parameters = self._split_where(where)

        sql = f"DELETE FROM {table}"
        sql += self._where(conditions) + self._returning(returning)
        cur = self.execute(sql, parameters)
        return cur.fetchall() if returning else cur.rowcount

    def execute(
            self,
            sql,
            params=None,
            fetch: Optional[Fetch] = None,
    ) -> Any:
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
        conditions, parameters = self._split_where(where)

        sql = self._select(table, fields, conditions, order, limit, offset)
        sql = f"copy ({sql}) to stdout with csv delimiter ',' header"
        sql = self._cursor.mogrify(sql, parameters)

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
        sqlify.create('my_table','id SERIAL PRIMARY KEY, name TEXT')"""
        self.execute("CREATE TABLE {} ({})".format(table, schema))

    def commit(self) -> None:
        """Commit a transaction"""
        self._cursor.connection.commit()

    def rollback(self) -> None:
        """Roll-back a transaction"""
        self._cursor.connection.rollback()

    def _format_insert(self, data):
        """Format insert dict values into strings"""
        cols = ", ".join(data.keys())
        vals = ", ".join([self._unnamed_parameter for k in data])

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
        return ", ".join(arguments)  # This removed the last comma in string

    def _split_where(self,
                     where: Optional[Union[str, List[str], Tuple[Union[List[str], str], Union[List, Dict]]]] = None) \
            -> Tuple[Union[str, List[str], None], Union[List, Dict, None]]:
        if not where:
            return (None, None)

        if not isinstance(where, tuple):
            return (where, None)

        if len(where) == 1:
            return (where[1], None)

        return (where[0], where[1])

    def _where(self, conditions: Optional[Union[List, str]] = None) -> str:
        if not conditions:
            return ""

        if isinstance(conditions, list):
            return f" WHERE {' AND '.join(conditions)}"

        return f" WHERE {conditions}"

    def _having(self, having: Optional[str] = None) -> str:
        if not having:
            return ""

        return f" HAVING {having}"

    def _with_sq(self, with_sq: Optional[Dict[str, str]] = None) -> str:
        if not with_sq:
            return ""

        return "WITH " + ", ".join(
            [f"{key} as ({value})" for key, value in with_sq.items()]
        )

    def _group(self, group: Optional[Union[List[str], str]] = None) -> str:
        if not group:
            return ""

        if isinstance(group, list):
            return f" GROUP BY {', '.join(group)}"

        return f" GROUP BY {group} "

    def _order(self, order: Optional[Union[str, Tuple[str, Union[Order, str]]]] = None) -> str:
        if not order:
            return ""

        if isinstance(order, str):
            return f" ORDER BY {order}"

        # If order is not a string, then it must be a tuple, here we just need to check the type of the 2º parameter
        if isinstance(order[1], str):
            return f" ORDER BY {order[0]} {order[1]}"

        # Second parameter must be of type Order
        return f" ORDER BY {order[0]} {order[1].value}"

    def _limit(self, limit: Optional[int]) -> str:
        if limit:
            return f" LIMIT {limit}"
        return ""

    def _offset(self, offset: Optional[int]) -> str:
        if offset:
            return f" OFFSET {offset}"
        return ""

    def _returning(self, returning: Optional[Union[str, List[str]]]) -> str:
        if not returning:
            return ""

        if isinstance(returning, list):
            return f" RETURNING {', '.join(returning)}"

        return f" RETURNING {returning}"

    def _fields(self, fields: Union[str, List[str]]) -> str:
        if isinstance(fields, str):
            return fields

        # It must be a list of strings
        return ', '.join(fields)

    def _select(
            self, table=None, fields=(), where=None, group=None, having=None, order=None, limit=None, offset=None,
            with_sq=None
    ) -> str:
        return (
                self._with_sq(with_sq)
                + f"SELECT {self._fields(fields)} FROM {table}"
                + self._where(where)
                + self._group(group)
                + self._having(having)
                + self._order(order)
                + self._limit(limit)
                + self._offset(offset)
        )

    def __del__(self):
        try:
            self._cursor.close()
        except Exception as e:  # TODO: Narrow down this exception
            if "Cannot operate on a closed database." not in str(e):
                raise e


class Psycopg2Sqlify(BaseSqlify):
    _unnamed_parameter = "%s"

    def _format_parameter(self, parameter: str) -> str:
        return f"%({parameter})s"


class Sqlite3Sqlify(BaseSqlify):
    _unnamed_parameter = "?"

    def _format_parameter(self, parameter: str) -> str:
        return f":{parameter}"
