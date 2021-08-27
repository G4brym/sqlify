import sqlite3

from sqlify import Session

if __name__ == "__main__":
    conn = sqlite3.connect('test.db')

    with Session(conn, autocommit=True) as sqlify:
        rest = sqlify.fetchone(
            table="test",
            fields="column_1",
        )
        print(rest)
        #
        # rest = sqlify.insert(
        #     table="test",
        #     data={"column_1": "test2"}
        # )
        # sqlify.commit()


        # rest = sqlify.update(
        #     table="test",
        #     data={"column_1": "test3"},
        #     where=("column_1 = 'test2'", None)
        # )
        # sqlify.commit()
        print(rest)

