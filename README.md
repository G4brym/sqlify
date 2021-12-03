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

The `sqlify` module provides:

* Python typed interface that can scale from just basic queries to some complex queries, for example using the
[PostgreSQL With](https://www.postgresql.org/docs/9.1/queries-with.html)
* Python API to wrap basic SQL functionality: select, update, delete, join et al
* Query results as python dict objects
* Inserts/Updates/Deletes returning data as dict objects or the affected rows count
* Error detection while coding due to the type hints (if you use a smart IDE like pycharm)
* Auto commit/rollback when finishing one or multiple queries
* Database migration tools (WIP)
* Bulk insert (WIP)
* Debug logging support


## Installation

With `pip` or `easy_install`:

```pip install sqlify```

or:

```easy_install sqlify```

or from the source:

```python setup.py install```


## 30 Seconds Quick-start Guide

* Step 1: Connect to the database of your choice
* Step 2: Using the Session class pass through the connection
* Step 3: Enjoy your queries

Here's a pseudo-example to illustrate the basic concepts:

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


## Basic Usage

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

If you don't like context based interfaces (aka [with statement](https://www.geeksforgeeks.org/with-statement-in-python/))
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

### Fetching a single record

```python
with Session(conn, autocommit=True) as sqlify:
    book = sqlify.fetchone(
        table='books', 
        fields="*",
        where=(
            "published = %(publish_date)s",
            dict(
                publish_date=datetime.date(2002, 2, 1),
            ),
        ),
    )
                   
print(f"{book.name} was published on {book.published}")
```

### Fetching multiple records

```python
from sqlify import Order

with Session(conn, autocommit=True) as sqlify:
    books = sqlify.fetchone(
        table='books',
        fields=['name AS n', 'genre AS g'],
        where=(
            "published BETWENN %(since)s and %(to)s",
            dict(
                since=datetime.date(2005, 2, 1),
                to=datetime.date(2009, 2, 1),
            ),
        ),
        order=("published", Order.DESC),
        limit=5,
        offset=2,
    )

for book in books:
    print(f"{book.name} was published on {book.published}")
```

### Raw SQL execution

In raw queries you can use both `list` and `dict` annotations

```python
with Session(conn, autocommit=True) as sqlify:
    sqlify.execute('SELECT tablename FROM pg_tables WHERE schemaname=%s and tablename=%s', ['public', 'books'])
    sqlify.execute('SELECT name FROM books WHERE author=%(author)s', {"author": "Andre"})
```

## WIP down from here

### Inserting rows

```python
for i in range(1, 10):
    db.insert("books",
              {"genre": "fiction",
               "name": "Book Name vol. %d" % i,
               "price": 1.23 * i,
               "published": "%d-%d-1" % (2000 + i, i)})

db.commit()
```

### Updating rows

```python
with pg_simple.PgSimple(connection_pool) as db1:
    db1.update('books',
               data={'name': 'An expensive book',
                     'price': 998.997,
                     'genre': 'non-fiction',
                     'modified': 'NOW()'},
               where=('published = %s', [datetime.date(2001, 1, 1)]))
               
    db1.commit()
```

### Deleting rows

```python
db.delete('books', where=('published >= %s', [datetime.date(2005, 1, 31)]))
db.commit()
```

### Dropping and creating tables

```python
db.drop('books')

db.create('books',
          '''
"id" SERIAL NOT NULL,
"type" VARCHAR(20) NOT NULL,
"name" VARCHAR(40) NOT NULL,
"price" MONEY NOT NULL,
"published" DATE NOT NULL,
"modified" TIMESTAMP(6) NOT NULL DEFAULT now()
'''
)

db.execute('''ALTER TABLE "books" ADD CONSTRAINT "books_pkey" PRIMARY KEY ("id")''')
db.commit()

```

### Emptying a table or set of tables

```python
db.truncate('tbl1')
db.truncate('tbl2, tbl3', restart_identity=True, cascade=True)
db.commit()
```

### Inserting/updating/deleting rows with return value

```python
row = db.insert("books",
                {"type": "fiction",
                 "name": "Book with ID",
                 "price": 123.45,
                 "published": "1997-01-31"},
                returning='id')
print(row.id)

rows = db.update('books',
                 data={'name': 'Another expensive book',
                       'price': 500.50,
                       'modified': 'NOW()'},
                 where=('published = %s', [datetime.date(2006, 6, 1)]),
                 returning='modified')
print(rows[0].modified)

rows = db.delete('books', 
                 where=('published >= %s', [datetime.date(2005, 1, 31)]), 
                 returning='name')
for r in rows:
    print(r.name)
```

### Explicit database transaction management

```python
with pg_simple.PgSimple(connection_pool) as _db:
    try:
        _db.execute('Some SQL statement')
        _db.commit()
    except:
        _db.rollback()
```

### Implicit database transaction management

```python
with pg_simple.PgSimple(connection_pool) as _db:
    _db.execute('Some SQL statement')
    _db.commit()
```

The above transaction will be rolled back automatically should something goes awry.
