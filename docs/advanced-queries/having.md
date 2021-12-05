Currently the having field just supports receiving a single string, but you can insert there as many
conditions as you want

## Having with one condition

```python
with Session(conn, autocommit=True) as sqlify:
    rows = sqlify.fetchall(
        table='books', 
        fields=[
            "genre",
            "count(*) as total"
        ],
        group="genre",
        having="genre is not null",
    )

for row in rows:
    print(f"{row.genre} has {row.total} books")
```
