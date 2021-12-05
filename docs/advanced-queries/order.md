The order field can receive multiple inputs and all of them will result in the same query:

* just a single string (just the field)
* a tuple of a string + another string (field + orientation)
* a tuple of a string + an object from the Order Enum (field + orientation)

## Order by a single field with the default orientation

```python
with Session(conn, autocommit=True) as sqlify:
    rows = sqlify.fetchall(
        table='books', 
        fields=[
            "name",
            "price",
        ],
        order="price",
    )

for row in rows:
    print(f"{row.name} has a price of {row.price} usd")
```

## Order by a single field with the Order Enum orientation

```python
from sqlify import Order

with Session(conn, autocommit=True) as sqlify:
    rows = sqlify.fetchall(
        table='books',
        fields=[
            "name",
            "price",
        ],
        order=("revenue", Order.DESC),
    )

for row in rows:
    print(f"{row.name} has a price of {row.price} usd")
```

## Order by a single field with a string orientation

```python
from sqlify import Order

with Session(conn, autocommit=True) as sqlify:
    rows = sqlify.fetchall(
        table='books',
        fields=[
            "name",
            "price",
        ],
        order=("revenue", "DESC"),
    )

for row in rows:
    print(f"{row.name} has a price of {row.price} usd")
```
