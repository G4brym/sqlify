## Introduction

This migration system aims to be very simple and efficient.

That said, there are only 3 functionalities
 - Generate a new migration file
 - Show migrations that have not been applied yet
 - Apply the remaining migrations

If you want to take a look into the migration code, it is a bit over 100 lines, very compact.

In this basic usage it is only shown the raw functionalities that are called from within your application. But there is
already a Typer cli that you can use to execute all this actions from your terminal or from the server terminal.
Take a look in the [Typer cli documentation page](typer-cli.md).

By having the migration system separated from the cli commands, give much more flexibility, because only you know what's
best for your project, either write your own scripts or use other cli library, or in my case use with the 
[Typer cli](https://github.com/tiangolo/typer)

Other features of the system:
 - Migrations always have an associated number to it, to allow a sequential order.
 - You can always choose to apply a specific migration without having to apply the remaining.
 - There is also support for fake migrations, just like django, that marks the migration as applied, but didn't actually
run any sql on the database.
 - There is a table automatically generated that keep track of the applied migrations.


## Setup

To start using the migrations service you must first initialize a sqlify session and then pass it through with your
desired folder to place the sql migration.
```python
import psycopg2
from sqlify import Session, Migrations

conn = psycopg2.connect("host=localhost dbname=migrations_test user=postgres password=postgres")
sqlify = Session(conn, autocommit=True).session

migrations_service = Migrations(
    migrations_path="my_migrations_folder/",  # This can be an absolut path or relative
    sqlify=sqlify,
)
```


## Generating a new migration file

In order to generate a new migration file you can just call the `generate_migration()` function, like this
```python
migrations_service.make_migration()
```

This function will get your latest migration number that you have on your migrations folder and create a new file with
that number.

Here is the current migration naming convention `{migration_number}_{date}_{hour}.sql` and the final result would be
something like this `0001_20220118_1148.sql` (you can customize this naming in the `Migrations` class).

If you don't have any migrations yet, this function will create the folder at your specified location and will start
a migration number 0001.


## List remaining migrations

You can get a list of filenames for the migrations that have not been applied yet
```python
migrations_service.discover_migrations()
```

By default, this function will only return the unapplied migrations, but you can get all migrations with the parameter
`unapplied_only` as shown.

```python
migrations_service.discover_migrations(unapplied_only=False)
```


## Apply a migration

To apply a migration you must pass the filename of the migration you want to pass.

And there are 3 ways you can pass the migration filename:
 - Full name with extension `0001_20220118_1148.sql`
 - Full name without extension `0001_20220118_1148`
 - Migration number `1` or `0001`

Besides the filename you can optionally enable the fake feature. This will mark the migration as applied, but will not
execute its sql content.

```python
migrations_service.apply_migration(filename="1")
```

Usually you would call the `discover_migrations()` first and the use a for loop to apply all migration, like this
```python
migrations = migrations_service.discover_migrations()

for file in migrations:
    migrations_service.apply_migration(filename=file)
```

Remember that you can always stick to the already existing cli commands to interact with the migration system, in 
[this page](typer-cli.md).
