## Fetching a single record

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

## Fetching multiple records

```python
from sqlify import Order

with Session(conn, autocommit=True) as sqlify:
    books = sqlify.fetchone(
        table='books',
        fields=['name AS n', 'genre AS g'],
        where=(
            [
                "published BETWENN %(since)s and %(to)s",
                "gender = %(gender)s",
            ],
            dict(
                since=datetime.date(2005, 2, 1),
                to=datetime.date(2009, 2, 1),
                gender="fiction",
            ),
        ),
        order=("published", Order.DESC),
        limit=5,
        offset=2,
    )

for book in books:
    print(f"{book.name} was published on {book.published}")
```

## Raw SQL execution

In raw queries you can use both `list` and `dict` annotations

```python
with Session(conn, autocommit=True) as sqlify:
    sqlify.execute('SELECT tablename FROM pg_tables WHERE schemaname=%s and tablename=%s', ['public', 'books'])
    sqlify.execute('SELECT name FROM books WHERE author=%(author)s', {"author": "Andre"})
```

## Inserting rows

```python
with Session(conn, autocommit=True) as sqlify:
    for i in range(1, 10):
        sqlify.insert(
            table="books",
            data=dict(
                name=f"Book Name vol. {i}",
                price=1.23 * i,
                genre="fiction",
                published=f"{2000 + i}-{i}-1",
            ),
        )

    # DB commit is already called when the session context exits without any exception
    # You can disable this with autocommit=False
```

## Updating rows

```python
from sqlify import RawSQL

with Session(conn, autocommit=True) as sqlify:
    affected_rows = sqlify.update(
        table="books",
        where=(
            "published = %(published)s",
            dict(
                published=datetime.date(2001, 1, 1)
            ),
        ),
        data=dict(
            genre="non-fiction",
            modified=RawSQL("now()"),
        ),
    )
    
    # Commit is implicit
    
print(f"Lines updated in this query: {affected_rows}")
```

## Deleting rows

```python
with Session(conn, autocommit=True) as sqlify:
    deleted_rows = sqlify.delete(
        table="books",
        where=(
            "published >= %(published)s",
            dict(published=datetime.date(2005, 1, 31)),
        ),
    )

    # Commit is implicit

print(f"Lines deleted in this query: {deleted_rows}")
```

## Dropping and creating tables

```python
with Session(conn, autocommit=True) as sqlify:
    sqlify.drop('books')

    sqlify.create('books',
        '''
        "id" SERIAL NOT NULL,
        "type" VARCHAR(20) NOT NULL,
        "name" VARCHAR(40) NOT NULL,
        "price" MONEY NOT NULL,
        "published" DATE NOT NULL,
        "modified" TIMESTAMP(6) NOT NULL DEFAULT now()
        '''
    )

    sqlify.execute('''ALTER TABLE "books" ADD CONSTRAINT "books_pkey" PRIMARY KEY ("id")''')

    # Commit is implicit
```

## Emptying a table or set of tables

```python
with Session(conn, autocommit=True) as sqlify:
    sqlify.truncate('tbl1')
    sqlify.truncate('tbl2, tbl3', restart_identity=True, cascade=True)

    # Commit is implicit
```
