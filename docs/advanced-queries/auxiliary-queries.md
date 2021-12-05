The with_sq parameter leverages the [WITH Queries from postgres](https://www.postgresql.org/docs/9.1/queries-with.html)

## Selecting with auxiliary queries

```python
with Session(conn, autocommit=True) as sqlify:
    rows = sqlify.fetchall(
        table='orders', 
        fields=[
            "region",
            "book",
            "SUM(quantity) AS book_units",
            "SUM(amount) AS book_sales"
        ],
        where="region IN (SELECT region FROM top_regions)",
        group=[
            "region", 
            "book",
        ],
        with_sq=dict(
            regional_sales="""
                SELECT region, SUM(amount) AS total_sales
                FROM orders
                GROUP BY region
            """,
            top_regions="""
                SELECT region
                FROM regional_sales
                WHERE total_sales > (SELECT SUM(total_sales)/10 FROM regional_sales)
            """,
        ),
    )
```
