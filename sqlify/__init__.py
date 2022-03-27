"""A simple sql builder based on standard Python type hints"""

__version__ = '0.7.4'
__all__ = [
    "BaseSqlify",
    "Sqlite3Sqlify",
    "Psycopg2Sqlify",
    "Session",
    "Fetch",
    "Order",
    "DatabaseType",
    "Fetch",
    "Order",
    "DatabaseType",
    "Migrations",
    "build_typer_cli",
    "MigrationAlreadyAppliedException",
    "TyperNotFound",
]

from .builder import BaseSqlify, Sqlite3Sqlify, Psycopg2Sqlify
from .operators import SqlOperator, RawSQL, DecreaseSQL, IncreaseSQL
from .session import Session
from .value_objects import Fetch, Order, DatabaseType
from .exceptions import MigrationAlreadyAppliedException, TyperNotFound
from .migrations import Migrations
from .cli import build_typer_cli
