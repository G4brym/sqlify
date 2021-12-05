The field parameter can receive a string of a list of strings, you can use this to leverage your python code 
to don't have to join the string together

## Selecting with a string

```python
with Session(conn, autocommit=True) as sqlify:
    rows = sqlify.fetchall(
        table='books', 
        fields="*",  # This will select all fields
    )
```

```python
with Session(conn, autocommit=True) as sqlify:
    rows = sqlify.fetchall(
        table='books', 
        fields="name, price",  # Just selcte 2 fields
    )
```

## Selecting with a list of strings

```python
fields = ["name", "description"]

# Give a special price for a special customer
if customer.is_vip:
    fields.append("(price - max_discount) as price")
else:
    fields.append("price")

with Session(conn, autocommit=True) as sqlify:
    rows = sqlify.fetchall(
        table='books', 
        fields=fields,
    )
```
