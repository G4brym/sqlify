## Installation

With `pip` or `easy_install`:

```pip install sqlify```

or:

```easy_install sqlify```

or from the source:

```python setup.py install```

## Basic Usage

### Connecting to the sqlite3 database

```python
import sqlite3
from sqlify import Session

conn = sqlite3.connect('my_test.db')
with Session(conn, autocommit=True) as sqlify:
    rest = sqlify.fetchone(
        table="test",
        fields="column_1",
    )
```

### Connecting to the posgtresql server

The following snippet will connect to the posgtresql server and allocate a cursor:

```python
import psycopg2
from sqlify import Session

conn = psycopg2.connect("host=localhost dbname=test user=postgres password=postgres")
with Session(conn, autocommit=True) as sqlify:
    rest = sqlify.fetchone(
        table="test",
        fields="column_1",
    )
```

By default `psycopg2` generates result sets as `collections.namedtuple` objects (using `psycopg2.extras.NamedTupleCursor`).
But because `sqlify` is connection agnostic you can easily modify it to use the `DictCursor` that returns a `Dict` object

```python
import psycopg2
from psycopg2.extras import DictCursor

conn = psycopg2.connect("host=localhost dbname=test user=postgres password=postgres", cursor_factory=DictCursor)
```

## Usage without context statement

If you don't like context based (aka [with statement](https://www.geeksforgeeks.org/with-statement-in-python/))
or it doesn't fit your architecture you can also assign it to a variable and use it as you did expect.
But remember that by using it this way you lost the auto-commit/rollback feature and auto-close of the database connection

```python
sqlify = Session(conn, autocommit=True).session
rest = sqlify.fetchone(
    table="test",
    fields="column_1",
)

sqlify.commit()
sqlify.close()
```
