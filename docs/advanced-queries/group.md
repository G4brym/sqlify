The group field can receive a string or a list of strings

## Group by one field

```python
with Session(conn, autocommit=True) as sqlify:
    rows = sqlify.fetchall(
        table='books', 
        fields=[
            "author",
            "count(*) as total"
        ],
        group="author",
    )

for row in rows:
    print(f"{row.author} published {row.total} books")
```

## Group by more than one field

```python
with Session(conn, autocommit=True) as sqlify:
    rows = sqlify.fetchall(
        table='books', 
        fields=[
            "author",
            "publisher",
            "count(*) as total"
        ],
        group=[
            "author",
            "publisher",
        ],
    )

for row in rows:
    print(f"{row.author} published {row.total} books with the published {row.publisher}")
```
