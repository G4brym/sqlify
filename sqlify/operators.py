class SqlOperator:
    pass


class RawSQL(SqlOperator, str):
    pass


class IncreaseSQL(SqlOperator, float):
    pass


class DecreaseSQL(SqlOperator, float):
    pass
