# [Sqlify](https://github.com/g4brym/Sqlify)
This project is a fork from [pg_simple](https://github.com/masroore/pg_simple), that tries to implement a standard SQL
with python type hinting interface.
This fork also implements extra parameters like having or with queries.
Other goals for this project is to support other types of databases like sqlite.

The [Sqlify](https://github.com/g4brym/Sqlify) module provides a simple standardized interface while keeping the
benefits and speed of using raw queries over `psycopg2` or `sqlite3`
This module is ment to work as a query builder, and you must provide your own integrations and session pooling if you want.

`sqlify` is not intended to provide ORM-like functionality, rather to make it easier to interact with the database from
python code for direct SQL access using convenient wrapper methods.

---

The `sqlify` module provides:

* Python typed interface that can scale from just basic queries to some complex queries, for example using the
  [PostgreSQL With](https://www.postgresql.org/docs/9.1/queries-with.html)
* Python API to wrap basic SQL functionality: select, update, delete, join et al
* Query results as python dict objects
* Inserts/Updates/Deletes returning data as dict objects or the affected rows count
* Auto commit/rollback when finishing one or multiple queries
* Database migration tools
* Typer cli for migration commands
* Bulk insert (WIP)
* On the fly error prevention when developing with a smart IDE like pycharm (due to the advanced type hinting)
* Debug logging support
