from unittest import TestCase, mock

from sqlify import Psycopg2Sqlify, RawSQL, IncreaseSQL, DecreaseSQL, Order


class TestBuilder(TestCase):
    table_name = "test_table"

    def setUp(self):
        self.cursor = mock.MagicMock()
        self.logger = mock.MagicMock()

        self.sqlify = Psycopg2Sqlify(
            self.cursor,
            self.logger,
        )

    def assertQuery(self, sql: str):
        query = str(self.cursor.execute.call_args[0][0]).lower()
        sql = sql.format(
            table=self.table_name,
        )

        self.cursor.execute.assert_called_once()
        self.assertEqual(query, sql)

    def test_fetchall_multiple_field(self):
        self.sqlify.fetchall(self.table_name, fields=["bonus", "ts"])

        self.assertQuery("select bonus, ts from {table}")

    def test_fetchall_single_field(self):
        self.sqlify.fetchall(self.table_name, fields="bonus")

        self.assertQuery("select bonus from {table}")

    def test_fetchone_single_field(self):
        self.sqlify.fetchone(self.table_name, fields="bonus")

        self.assertQuery("select bonus from {table} limit 1")

    def test_fetchall_where_single_condition(self):
        self.sqlify.fetchall(
            self.table_name,
            fields="bonus",
            where=(
                "bonus_key = %(bonus_key)s",
                dict(),
            ),
        )

        self.assertQuery("select bonus from {table} where bonus_key = %(bonus_key)s")

    def test_fetchall_where_list_of_conditions(self):
        self.sqlify.fetchall(
            self.table_name,
            fields="bonus",
            where=(
                [
                    "bonus_key = %(bonus_key)s",
                    "ts = %(ts)s",
                ],
                dict(),
            ),
        )

        self.assertQuery(
            "select bonus from {table} where bonus_key = %(bonus_key)s "
            "and ts = %(ts)s"
        )

    def test_fetchall_where_conditions_limit_and_offset(self):
        self.sqlify.fetchall(
            self.table_name,
            fields="bonus",
            where=(
                [
                    "bonus_key = %(bonus_key)s",
                    "ts = %(ts)s",
                ],
                dict(),
            ),
            limit=5,
            offset=10,
        )

        self.assertQuery(
            "select bonus from {table} where bonus_key = %(bonus_key)s "
            "and ts = %(ts)s limit 5 offset 10"
        )

    def test_fetchall_where_conditions_order_by(self):
        self.sqlify.fetchall(
            self.table_name,
            fields="bonus",
            where=(
                [
                    "bonus_key = %(bonus_key)s",
                    "ts = %(ts)s",
                ],
                dict(),
            ),
            order=("id", Order.ASC),
        )

        self.assertQuery(
            "select bonus from {table} where bonus_key = %(bonus_key)s "
            "and ts = %(ts)s order by id asc"
        )

    def test_fetchall_where_conditions_order_by_desc(self):
        self.sqlify.fetchall(
            self.table_name,
            fields="bonus",
            where=(
                [
                    "bonus_key = %(bonus_key)s",
                    "ts = %(ts)s",
                ],
                dict(),
            ),
            order=("id", Order.DESC),
        )

        self.assertQuery(
            "select bonus from {table} where bonus_key = %(bonus_key)s "
            "and ts = %(ts)s order by id desc"
        )

    def test_fetchall_where_conditions_order_by_desc_raw(self):
        self.sqlify.fetchall(
            self.table_name,
            fields="bonus",
            where=(
                [
                    "bonus_key = %(bonus_key)s",
                    "ts = %(ts)s",
                ],
                dict(),
            ),
            order=("id", "DESC"),
        )

        self.assertQuery(
            "select bonus from {table} where bonus_key = %(bonus_key)s "
            "and ts = %(ts)s order by id desc"
        )

    def test_insert(self):
        self.sqlify.insert(self.table_name, data=dict(asd="test", ts="123"))

        self.assertQuery("insert into {table} (asd, ts) values(%s, %s)")

    def test_insert_returning_everything(self):
        self.sqlify.insert(
            self.table_name,
            data=dict(asd="test", ts="123"),
            returning="*",
        )

        self.assertQuery("insert into {table} (asd, ts) values(%s, %s) returning *")

    def test_update_no_conditions(self):
        self.sqlify.update(self.table_name, data=dict(asd="test", ts="123"))

        self.assertQuery(
            "update test_table set asd = %(asd_datainput)s, ts = %(ts_datainput)s"
        )

    def test_update_with_conditions(self):
        self.sqlify.update(
            self.table_name,
            data=dict(asd="test", ts="123"),
            where=(
                [
                    "bonus_key = %(bonus_key)s",
                    "ts = %(ts)s",
                ],
                dict(),
            ),
        )

        self.assertQuery(
            "update test_table set asd = %(asd_datainput)s, "
            "ts = %(ts_datainput)s "
            "where bonus_key = %(bonus_key)s and ts = %(ts)s"
        )

    def test_update_with_raw_sql_conditions(self):
        self.sqlify.update(
            self.table_name,
            where=(
                ["id = %(id)s", "end_date > now() at time zone 'utc'"],
                dict(id=1),
            ),
            data=dict(
                end_date=RawSQL("now() at time zone 'utc'"),
            ),
        )

        self.assertQuery(
            "update test_table set end_date = now() at time zone 'utc' "
            "where id = %(id)s and end_date > now() at time zone 'utc'"
        )

    def test_update_with_increase_sql(self):
        self.sqlify.update(
            self.table_name,
            data=dict(
                earned=IncreaseSQL(10),
            ),
        )

        self.assertQuery("update test_table set earned = earned + %(earned_datainput)s")

    def test_update_with_decrease_sql(self):
        self.sqlify.update(
            self.table_name,
            data=dict(
                earned=DecreaseSQL(10),
            ),
        )

        self.assertQuery("update test_table set earned = earned - %(earned_datainput)s")

    def test_update_with_conditions_returning_everything(self):
        self.sqlify.update(
            self.table_name,
            data=dict(asd="test", ts="123"),
            where=(
                [
                    "bonus_key = %(bonus_key)s",
                    "ts = %(ts)s",
                ],
                dict(),
            ),
            returning="*",
        )

        self.assertQuery(
            "update test_table set asd = %(asd_datainput)s, ts = %(ts_datainput)s "
            "where bonus_key = %(bonus_key)s and ts = %(ts)s "
            "returning *"
        )

    def test_delete_no_conditions(self):
        self.sqlify.delete(
            self.table_name,
        )

        self.assertQuery("delete from test_table")

    def test_delete_with_conditions(self):
        self.sqlify.delete(
            self.table_name,
            where=(
                [
                    "bonus_key = %(bonus_key)s",
                    "ts = %(ts)s",
                ],
                dict(),
            ),
        )

        self.assertQuery(
            "delete from test_table where bonus_key = %(bonus_key)s and ts = %(ts)s"
        )

    def test_delete_with_conditions_returning_everything(self):
        self.sqlify.delete(
            self.table_name,
            where=(
                [
                    "bonus_key = %(bonus_key)s",
                    "ts = %(ts)s",
                ],
                dict(),
            ),
            returning="*",
        )

        self.assertQuery(
            "delete from test_table where bonus_key = %(bonus_key)s "
            "and ts = %(ts)s returning *"
        )
