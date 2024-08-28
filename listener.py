from telegram import Update, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, Application

from meeting import Meeting
from participants import Participants
from utils import (
    add_participant,
    generate_participants_keyboard,
    generate_meeting_string,
)
from constants import (
    MEETING_CANCEL,
    MEETING_EDIT,
    MEETING_READY,
    NOTIFY_ACCEPT,
    NOTIFY_LATE,
    NOTIFY_REJECT,
    REJECT_REGISTRATION,
    SUCCESS_REGISTRATION,
    SELECT_PARTICIPANTS_PREFIX,
    UNSELECT_PARTICIPANTS_PREFIX,
    NOTIFY_PREFIX,
)


class Listener:
    def __init__(
        self, meeting: Meeting, participants_state: Participants, app: Application
    ):
        self.app = app
        self.participants_state = participants_state
        self.meeting = meeting

    async def notify_button_listener(self, query: CallbackQuery) -> None:
        if query.data.startswith(NOTIFY_PREFIX):
            _, username, status = query.data.split(" ")

            if status == NOTIFY_ACCEPT:
                await self.app.bot.send_message(
                    chat_id=self.meeting.admin["chat_id"],
                    text=f"@{username} согласен",
                )

            if status == NOTIFY_LATE:
                await self.app.bot.send_message(
                    chat_id=self.meeting.admin["chat_id"],
                    text=f"@{username} опоздает",
                )

            if status == NOTIFY_REJECT:
                await self.app.bot.send_message(
                    chat_id=self.meeting.admin["chat_id"], text=f"@{username} отказался"
                )

            await query.edit_message_text("Отлично, уведомил администратора")

    async def apply_meeting_buttons_listener(self, query: CallbackQuery) -> None:
        if query.data == MEETING_READY:
            await self.meeting.notify_participants(self.app)
            await query.edit_message_text("Встреча создана")
        elif query.data == MEETING_CANCEL:
            self.meeting.reset()
            await query.edit_message_text("Встреча отменена")
        elif query.data == MEETING_EDIT:
            # TODO
            await query.edit_message_text(
                "Встреча отредактирована",
            )

    async def registration_buttons_listener(self, query: CallbackQuery) -> None:
        if query.data == SUCCESS_REGISTRATION:
            add_participant(query.from_user.username, query.message.chat.id)
            await query.edit_message_text("Отлично, я записал тебя")
        elif query.data == REJECT_REGISTRATION:
            await query.edit_message_text("Нет, ну так не пойдёт")

    async def participants_buttons_listener(self, query: CallbackQuery) -> None:
        if query.data.startswith(SELECT_PARTICIPANTS_PREFIX) or query.data.startswith(
            UNSELECT_PARTICIPANTS_PREFIX
        ):
            status, username = query.data.split(" ")
            if status == UNSELECT_PARTICIPANTS_PREFIX:
                self.participants_state.select_participant(username)

            else:
                self.participants_state.unselect_participant(username)

            keyboard = generate_participants_keyboard(
                self.meeting.admin, self.participants_state.participants
            )
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_reply_markup(reply_markup=reply_markup)

    async def button_listener(
        self, update: Update, _context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        query = update.callback_query

        await query.answer()

        await self.notify_button_listener(query)
        await self.apply_meeting_buttons_listener(query)
        await self.registration_buttons_listener(query)
        await self.participants_buttons_listener(query)
