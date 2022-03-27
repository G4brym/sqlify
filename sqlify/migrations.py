import itertools
import os
from datetime import datetime
from typing import List

from .exceptions import MigrationAlreadyAppliedException

from .builder import BaseSqlify, Sqlite3Sqlify, Psycopg2Sqlify


class Migrations():
    def __init__(
            self,
            migrations_path: str,
            sqlify: BaseSqlify,
            migration_name_template: str = "{migration_number}_{date}_{hour}.sql",
            migration_table_name: str = "db_migrations"
    ) -> None:
        self._migrations_path = migrations_path
        self._sqlify = sqlify

        self._migration_name_template = migration_name_template
        self._migration_table_name = migration_table_name

        self._init_migrations_table()

    def _init_migrations_table(self) -> None:
        if isinstance(self._sqlify, Sqlite3Sqlify):
            initial_migration = f"""
                CREATE TABLE IF NOT EXISTS {self._migration_table_name}
                (
                    id integer constraint table_name_pk primary key autoincrement,
                    name text,
                    applied_at timestamp default CURRENT_TIMESTAMP not null
                );
            """

        elif isinstance(self._sqlify, Psycopg2Sqlify):
            initial_migration = f"""
                CREATE TABLE IF NOT EXISTS {self._migration_table_name}
                (
                    id serial constraint {self._migration_table_name}_pk primary key,
                    name varchar(32) not null,
                    applied_at timestamp default timezone('utc'::text, now()) not null
                );
                
                CREATE UNIQUE INDEX IF NOT EXISTS {self._migration_table_name}_name_uindex
                    ON {self._migration_table_name} (name);
            """

        else:
            raise NotImplementedError()

        self._sqlify.execute(initial_migration)
        self._sqlify.commit()

    def _get_next_migration_number(self) -> int:
        next_migration_number = 0
        for (dirpath, dirnames, filenames) in os.walk(self._migrations_path):
            for filename in filenames:
                _number = filename.split("_")[0]
                next_migration_number = max(next_migration_number, int(_number))

        return next_migration_number +1

    def make_migration(self) -> str:
        now = datetime.now()
        migration_number = self._get_next_migration_number()

        filename = self._migration_name_template.format(
            migration_number=str(migration_number).zfill(4),
            date=now.strftime("%Y%m%d"),
            hour=now.strftime("%H%M"),
        )

        os.makedirs(self._migrations_path, exist_ok=True)
        with open(os.path.join(self._migrations_path, filename), "a") as f:
            f.write(f"-- Migration number: {migration_number} \t {now.strftime('%Y-%m-%d %H:%M')}\n")
            f.write("BEGIN;\n\n\n\nCOMMIT;\n")

        return str(os.path.join(self._migrations_path, filename))

    def discover_migrations(
            self, unapplied_only: bool = True
    ) -> List[str]:
        exclude = []
        if unapplied_only:
            exclude = self._sqlify.fetchall(
                table=self._migration_table_name,
                fields="name",
            )

            if len(exclude) > 0 and isinstance(exclude[0], dict):
                exclude = [
                    item.values()
                    for item in exclude
                ]

            exclude = list(itertools.chain.from_iterable(exclude))

        files = []
        for (dirpath, dirnames, filenames) in os.walk(self._migrations_path):
            for filename in filenames:

                if self.get_migration_name(filename) not in exclude:
                    files.append(filename)

        files.sort(key=lambda x: x.split(".")[0])
        return files

    def _get_migration_content(self, filename: str) -> str:
        with open(os.path.join(self._migrations_path, filename), "r") as f:
            return f.read()

    @staticmethod
    def get_migration_name(filename: str) -> str:
        filename = filename.lower()
        if filename.endswith(".sql") is False:
            return filename

        _contents = filename.split(".")
        return ".".join(_contents[:-1])

    def apply_migration(
            self, filename: str, fake: bool = False
    ) -> None:
        condition = "name = %(name)s"
        if isinstance(self._sqlify, Sqlite3Sqlify):
            condition = "name = :name"

        _already_applied = self._sqlify.fetchone(
            table=self._migration_table_name,
            fields="1",
            where=(
                condition,
                dict(name=self.get_migration_name(filename)),
            ),
        )

        if _already_applied is not None:
            raise MigrationAlreadyAppliedException(f"Migration {filename} is already applied!")

        if fake is False:
            # This can trow an exception, but it shouldn't be caught
            self._sqlify.execute(
                self._get_migration_content(filename)
            )

        self._sqlify.insert(
            "db_migrations", data=dict(name=self.get_migration_name(filename))
        )
        self._sqlify.commit()
