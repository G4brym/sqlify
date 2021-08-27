from enum import Enum


class Order(Enum):
    ASC = "ASC"
    DESC = "DESC"


class DatabaseType(Enum):
    PSYCOPG2 = "PSYCOPG2"
    SQLITE3 = "SQLITE3"


class Fetch(Enum):
    ONE = "ONE"
    ALL = "ALL"
