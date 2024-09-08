import psycopg
from psycopg import sql

from constants import (
    DEFAULT_ERROR,
    RECORD_ALREADY_EXIST,
)


class Db:
    def __init__(self, dbname: str, user: str, password: str, host: str, port: str):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port

        self.conn = psycopg.connect(
            f"dbname={self.dbname} user={self.user} host={self.host} password={self.password} port={self.port}"
        )
        self.cur = self.conn.cursor()

    def select(self, table: str, keys="*", conditions: tuple = None, mode: str = "all"):
        try:
            query = sql.SQL("SELECT {keys} FROM {table} {conditions}").format(
                keys=sql.SQL(", ").join(map(sql.SQL, keys)),
                table=sql.Identifier(table),
                conditions=(
                    sql.SQL("WHERE {conditions}").format(
                        conditions=sql.SQL(" AND ").join(
                            map(
                                lambda condition: sql.SQL("{}{}{}").format(
                                    sql.SQL(condition[0]),
                                    sql.SQL(condition[1]),
                                    sql.Literal(condition[2]),
                                ),
                                conditions,
                            )
                        )
                    )
                    if conditions
                    else sql.SQL("")
                ),
            )
            self.cur.execute(
                query,
            )
            if mode == "all":
                return self.cur.fetchall()

            return self.cur.fetchone()
        except Exception as e:
            print(e)
            raise Exception(DEFAULT_ERROR)

    def insert(self, table: str, keys: tuple, values: tuple, returning=None):
        try:
            query = sql.SQL(
                "INSERT INTO {table} ({keys}) VALUES ({values}) {returning}"
            ).format(
                table=sql.Identifier(table),
                keys=sql.SQL(", ").join(map(sql.SQL, keys)),
                values=sql.SQL(", ").join(sql.Placeholder() * len(keys)),
                returning=(
                    sql.SQL("RETURNING {returning}").format(
                        returning=sql.SQL(returning)
                    )
                    if returning
                    else sql.SQL("")
                ),
            )
            self.cur.execute(
                query,
                values,
            )
            self.conn.commit()
            if returning:
                return self.cur.fetchone()[0]
        except psycopg.IntegrityError as e:
            print(e)
            self.conn.commit()
            if e.sqlstate == "23505":  # UniqueViolation sqlstate code
                raise Exception(RECORD_ALREADY_EXIST)
            else:
                raise Exception(DEFAULT_ERROR)
        except Exception:
            self.conn.commit()
            raise Exception(DEFAULT_ERROR)

    def delete(self, table: str, conditions: tuple, returning=None):
        try:
            query = sql.SQL("DELETE FROM {table} {conditions} {returning}").format(
                table=sql.Identifier(table),
                conditions=(
                    sql.SQL("WHERE {conditions}").format(
                        conditions=sql.SQL(" AND ").join(
                            map(
                                lambda condition: sql.SQL("{}{}{}").format(
                                    sql.SQL(condition[0]),
                                    sql.SQL(condition[1]),
                                    sql.Literal(condition[2]),
                                ),
                                conditions,
                            )
                        )
                    )
                    if conditions
                    else sql.SQL("")
                ),
                returning=(
                    sql.SQL("RETURNING {returning}").format(
                        returning=sql.SQL(returning)
                    )
                    if returning
                    else sql.SQL("")
                ),
            )
            self.cur.execute(query)
            self.conn.commit()
            if returning:
                return self.cur.fetchone()[0]
        except Exception as e:
            self.conn.commit()
            print(e)
            raise Exception(DEFAULT_ERROR)

    def update(self, table: str, keys_values: tuple, conditions: tuple, returning=None):
        try:
            query = sql.SQL(
                "UPDATE {table} SET {keys_values} {conditions} {returning}"
            ).format(
                table=sql.Identifier(table),
                keys_values=sql.SQL(", ").join(
                    map(
                        lambda key_value: sql.SQL("{}={}").format(
                            sql.SQL(key_value[0]), sql.Literal(key_value[1])
                        ),
                        keys_values,
                    )
                ),
                conditions=(
                    sql.SQL("WHERE {conditions}").format(
                        conditions=sql.SQL(" AND ").join(
                            map(
                                lambda condition: sql.SQL("{}{}{}").format(
                                    sql.SQL(condition[0]),
                                    sql.SQL(condition[1]),
                                    sql.Literal(condition[2]),
                                ),
                                conditions,
                            )
                        )
                    )
                    if conditions
                    else sql.SQL("")
                ),
                returning=(
                    sql.SQL("RETURNING {returning}").format(
                        returning=sql.SQL(returning)
                    )
                    if returning
                    else sql.SQL("")
                ),
            )
            self.cur.execute(query)
            self.conn.commit()
            if returning:
                return self.cur.fetchone()
        except Exception:
            self.conn.commit()
            raise Exception(DEFAULT_ERROR)

    def custom_query(self, query: str):
        try:
            self.cur.execute(query)
            self.conn.commit()
            return self.cur.fetchall()
        except Exception:
            self.conn.commit()
            raise Exception(DEFAULT_ERROR)


def close(self):
    self.cur.close()
    self.conn.close()
