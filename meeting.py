from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application

from constants import NOTIFY_ACCEPT, NOTIFY_LATE, NOTIFY_REJECT, NOTIFY_PREFIX
from utils import generate_meeting_string


class Meeting:
    def __init__(self):
        self.admin = {}
        self.theme = ""
        self.date = ""
        self.participants = []

    def add_participant(self, participant):
        self.participants.append(participant)

    def remove_participant(self, participant):
        self.participants.remove(participant)

    def set_theme(self, theme: str):
        self.theme = theme

    def set_date(self, date: str):
        self.date = date

    def set_admin(self, username: str, chat_id: int):
        self.admin = {"username": username, "chat_id": chat_id}

    def reset(self):
        self.theme = ""
        self.date = ""
        self.participants = []

    async def notify(self, app: Application, chat_id: int, username: str):
        meeting_string = generate_meeting_string(
            self.admin["username"],
            self.theme,
            self.date,
            self.participants,
        )

        callback_data_accept = f"{NOTIFY_PREFIX} {username} {NOTIFY_ACCEPT}"
        callback_data_late = f"{NOTIFY_PREFIX} {username} {NOTIFY_LATE}"
        callback_data_reject = f"{NOTIFY_PREFIX} {username} {NOTIFY_REJECT}"

        keyboard = (
            [
                InlineKeyboardButton(
                    "Принять", callback_data=f"{callback_data_accept}"
                ),
                InlineKeyboardButton("Опоздаю", callback_data=f"{callback_data_late}"),
                InlineKeyboardButton(
                    "Отклонить", callback_data=f"{callback_data_reject}"
                ),
            ],
        )

        reply_markup = InlineKeyboardMarkup(keyboard)

        await app.bot.send_message(
            chat_id=chat_id,
            text=meeting_string,
            reply_markup=reply_markup,
            parse_mode="HTML",
        )

    async def notify_participants(self, app: Application):
        for participant in self.participants:
            await self.notify(app, participant["chat_id"], participant["username"])
