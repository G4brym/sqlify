import itertools
import os
from datetime import datetime
from typing import List

from .exceptions import MigrationAlreadyAppliedException

from .builder import BaseSqlify


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

    def make_migration(self) -> str:
        now = datetime.now()
        migration_number = len(self.discover_migrations(unapplied_only=False)) + 1

        filename = self._migration_name_template.format(dict(
            migration_number=migration_number,
            date=now.strftime("%Y%m%d"),
            hour=now.strftime("%H%M"),
        ))

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
        _already_applied = self._sqlify.fetchone(
            table=self._migration_table_name,
            fields="1",
            where=(
                "name = %(name)s",
                dict(name=self.get_migration_name(filename)),
            ),
        )

        if _already_applied is not None:
            raise MigrationAlreadyAppliedException(f"Migration {filename} is already applied!")

        if not fake:
            # This can trow an exception, but it shouldn't be caught
            self._sqlify.execute(
                self._get_migration_content(filename)
            )

        self._sqlify.insert(
            "db_migrations", data=dict(name=self.get_migration_name(filename))
        )
        self._sqlify.commit()
