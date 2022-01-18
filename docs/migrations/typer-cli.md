## Introduction

Besides, having the raw migration system, the sqlify already includes a basic command line interface using the
[Typer library](https://github.com/tiangolo/typer).

All you need to do is initialize the `Migrations` class the call the cli builder with it, then just attach the result
in your cli.

Here is a full example of it, in a file named `cli.py`

```python
import psycopg2
from sqlify import Session, build_typer_cli, Migrations

import typer


conn = psycopg2.connect("host=localhost dbname=migrations_test user=postgres password=postgres")
sqlify = Session(conn, autocommit=True).session

migrations_service = Migrations(
    migrations_path="my_migrations_folder/",
    sqlify=sqlify,
)

app = typer.Typer()
app.add_typer(build_typer_cli(migrations_service=migrations_service), name="db")

if __name__ == "__main__":
    app()
```

Then all you need to do is call the script with the defined section name `db` in this case

Execute `python cli.py db` and you will the the command list
```bash
$ python cli.py db
Usage: cli.py db [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  make-migration
  migrate
  show-migrations
```


## Generating a new migration file

To generate a new migration you just need to call the make-migration command
```bash
$ python cli.py db make-migration
my_migrations_folder/0001_20220118_1830.sql Created
```


## List remaining migrations

This command will only list migration that have not been applied yet
```bash
$ python cli.py db show-migrations
Migrations to apply:
 - 0001_20220118_1830
 - 0002_20220118_1831
```


## Apply all missing migrations

This command will always prompt for confirmation before executing any sql code, and it will also display what migrations
will be applied
```bash
$ python cli.py db migrate
Migrations to apply:
 - 0001_20220118_1830
 - 0002_20220118_1831
Are you sure you want to continue? [y/N]: 
```

After confirmation the command will output the applied migrations again
```bash
$ python cli.py db migrate
Migrations to apply:
 - 0001_20220118_1830
 - 0002_20220118_1831
Are you sure you want to continue? [y/N]: y
[0001_20220118_1830] Migration Applied
[0002_20220118_1831] Migration Applied
```


## Apply a single migration

To apply a migration you must pass the filename of the migration you want to pass.

And there are 3 ways you can pass the migration filename:
- Full name with extension `0001_20220118_1148.sql`
- Full name without extension `0001_20220118_1148`
- Migration number `1` or `0001`

As before, the command will always display what is going to happen and wait for confirmation before any sql 
is executed.

```bash
$ python cli.py db migrate --filename 2
Migrations to apply:
 - 0002_20220118_1831
Are you sure you want to continue? [y/N]: y
[0002_20220118_1831] Migration Applied
```


## Apply a fake migration

Sometimes to archive 0 downtime when deploying we need to execute some sql changes before even starting the deploy
this parameters help with just that.

This way you can execute the migrations manually in the db, and when there's time to sync up, you can call the migrate
command with the `--fake` paramter to just mark the migrations as applied without running the actual sql code.

As before, you can run this with a single migration, by passing the filename, or with all the remaining migrations

The command will also print a warning in the terminar to let you know that no sql code will be run.

```bash
$ python cli.py db migrate --fake
FAKE is Active
Migrations to apply:
 - 0001_20220118_1830
 - 0002_20220118_1831
Are you sure you want to continue? [y/N]: y
[0001_20220118_1830] Migration Applied
[0002_20220118_1831] Migration Applied
```
