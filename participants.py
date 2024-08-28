from constants import SELECT_PARTICIPANTS_PREFIX, UNSELECT_PARTICIPANTS_PREFIX
from utils import generate_participants


class Participants:
    def __init__(self):
        self._participants = self.get_default_participants()
        self.subscriptions = []

    @property
    def participants(self):
        return self._participants

    def get_default_participants(self):
        participants_raw = generate_participants()
        participants = {}
        for username, chat_id in participants_raw:
            participants[username] = {
                "username": username,
                "status": UNSELECT_PARTICIPANTS_PREFIX,
                "chat_id": chat_id,
            }

        return participants

    def notify(self, username):
        for callback in self.subscriptions:
            callback(self._participants[username])

    def select_participant(self, username):
        self._participants[username]["status"] = SELECT_PARTICIPANTS_PREFIX
        self.notify(username)

    def unselect_participant(self, username):
        self._participants[username]["status"] = UNSELECT_PARTICIPANTS_PREFIX
        self.notify(username)

    def get_selected_participants(self):
        return [
            participant
            for participant in self.participants
            if self.participants[participant["username"]]["status"]
            == SELECT_PARTICIPANTS_PREFIX
        ]

    def reset(self):
        self._participants = self.get_default_participants()

    def subscribe(self, callback):
        self.subscriptions.append(callback)
