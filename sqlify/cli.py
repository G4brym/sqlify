from typing import List, Optional

from .exceptions import TyperNotFound
from .migrations import Migrations

try:
    from typer import Typer
    import typer
except ModuleNotFoundError:
    Typer = None


def build_typer_cli(migrations_service: Migrations) -> Typer:
    if Typer is None:
        raise TyperNotFound("Typer dependency is not installed!")

    cli = Typer()

    def display_migrations(migrations: List[str]) -> None:
        for filename in migrations:
            typer.secho(
                f" - {migrations_service.get_migration_name(filename)}",
                fg=typer.colors.GREEN,
            )

    @cli.command()
    def show_migrations():
        migrations = migrations_service.discover_migrations()

        if len(migrations) == 0:
            typer.secho("No migrations to apply", fg=typer.colors.YELLOW)
            return

        typer.secho("Migrations to apply:", fg=typer.colors.GREEN)
        display_migrations(migrations)

    @cli.command()
    def make_migration():
        typer.secho(f"{migrations_service.make_migration()} Created", fg=typer.colors.GREEN)

    @cli.command()
    def migrate(filename: Optional[str] = None, fake: bool = False):
        migrations = migrations_service.discover_migrations()

        if filename is not None:
            if {filename, f"{filename}.sql", migrations_service.get_migration_name(filename)}.intersection(set(migrations)):
                migrations = [migrations_service.get_migration_name(filename)]
            elif filename.isdigit() and len([i for i in migrations if i.startswith(filename.zfill(4))]) > 0:
                migrations = [i for i in migrations if i.startswith(filename.zfill(4))]
            else:
                migrations = []

        if len(migrations) == 0:
            typer.secho("No migrations to apply", fg=typer.colors.YELLOW)
            return

        if fake is True:
            typer.secho("FAKE is Active", fg=typer.colors.BRIGHT_YELLOW)

        typer.secho("Migrations to apply:", fg=typer.colors.GREEN)
        display_migrations(migrations)

        _continue = typer.confirm("Are you sure you want to continue?")
        if _continue is False:
            typer.echo("No Migrations applied")
            raise typer.Abort()

        for file in migrations:
            migrations_service.apply_migration(filename=file, fake=fake)
            typer.secho(f"[{migrations_service.get_migration_name(file)}] Migration Applied", fg=typer.colors.GREEN)

    return cli
