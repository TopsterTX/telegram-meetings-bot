from constants import CREATING
from db import Db
from psycopg import sql


class Meeting:
    def __init__(self, db: Db):
        self._db = db

    def get_all_meetings(self):
        return self._db.select("meetings")

    def get_meeting_by_id(self, meeting_id):
        return self._db.select("meetings", "*", (("id", "=", meeting_id),))[0]

    def get_meeting_by_admin_id(self, admin_id):
        return self._db.select("meetings", "*", (("admin_user_id", "=", admin_id),))[0]

    def get_meeting_participants(self, meeting_id, keys: tuple = "*"):
        return self._db.custom_query(
            sql.SQL(
                "SELECT {keys} FROM users JOIN user_meeting AS um ON um.meeting_id={meeting_id} WHERE um.user_id=users.id"
            ).format(
                keys=sql.SQL(", ").join(map(sql.SQL, keys)),
                meeting_id=sql.Literal(meeting_id),
            )
        )

    def set_meeting_data(self, id: str, keys_values: tuple):
        return self._db.update("meetings", keys_values, (("id", "=", id),), "id")

    def set_status(self, id: str, status: str):
        return self.set_meeting_data(id, (("status", status),))

    def create_meeting(self, keys: tuple = ("status",), values: tuple = (CREATING,)):
        return self._db.insert("meetings", keys, values, "id")

    def delete_meeting(self, id: str):
        return self._db.delete("meetings", (("id", "=", id),), "id")

    def add_participant_to_meeting(self, meeting_id, user_id):
        return self._db.insert(
            "user_meeting",
            ("user_id", "meeting_id"),
            (user_id, meeting_id),
            "meeting_id",
        )

    def remove_participant_to_meeting(self, meeting_id, user_id):
        return self._db.delete(
            "user_meeting", (("meeting_id", "=", meeting_id), ("user_id", "=", user_id))
        )
