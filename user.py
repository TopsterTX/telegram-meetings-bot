from db import Db


class User:
    def __init__(self, db: Db):
        self._db = db

    def get_users(self, conditions: tuple = None):
        return self._db.select("users", "*", conditions, "all")

    def get_user_by_username(self, username):
        return self._db.select("users", "*", (("username", "=", username),), "one")

    def get_user_by_chat_id(self, chat_id):
        return self._db.select("users", "*", (("chat_id", "=", chat_id),), "one")

    def get_user_by_id(self, user_id):
        return self._db.select("users", "*", (("id", "=", user_id),), "one")

    def create_user(self, keys: tuple, values: tuple):
        return self._db.insert("users", keys, values, "id")

    def delete_user(self, user_id: str):
        return self._db.delete("users", (("id", "=", user_id),), "id")
