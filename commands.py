from telegram.ext import ContextTypes, ConversationHandler, Application
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
)

from constants import (
    MEETING_CANCEL,
    MEETING_READY,
)
from meeting import Meeting
from participants import Participants
from utils import generate_participants_keyboard, generate_meeting_string


class Commands:
    def __init__(
        self, meeting: Meeting, participants_state: Participants, app: Application
    ):
        self.app = app
        self.meeting = meeting
        self.participants_state = participants_state
        self.THEME, self.DATE, self.PARTICIPANTS = range(0, 3)

    async def create_meeting(
        self, update: Update, _context: ContextTypes.DEFAULT_TYPE
    ) -> None:

        admin_username = update.message.from_user.username
        admin_chat_id = update.message.chat.id
        self.meeting.set_admin(admin_username, admin_chat_id)

        await update.message.reply_text(
            f"Админ: {admin_username}\nУкажите тему встречи:"
        )

        return self.THEME

    async def get_theme(
        self, update: Update, _context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        theme = update.message.text
        self.meeting.set_theme(theme)

        await update.message.reply_text("Укажите дату встречи (dd.mm.yyyy hh:mm):")

        return self.DATE

    async def get_date(
        self, update: Update, _context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        date = update.message.text
        self.meeting.set_date(date)

        keyboard = generate_participants_keyboard(
            admin=self.meeting.admin, participants=self.participants_state.participants
        )
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "Выберите участников:", reply_markup=reply_markup
        )

        return self.PARTICIPANTS

    async def get_participants_and_apply(
        self, update: Update, _context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        await update.callback_query.answer()

        meeting_string = generate_meeting_string(
            self.meeting.admin["username"],
            self.meeting.theme,
            self.meeting.date,
            self.meeting.participants,
        )
        keyboard = (
            [
                InlineKeyboardButton("Готово", callback_data=MEETING_READY),
                InlineKeyboardButton("Отмена", callback_data=MEETING_CANCEL),
            ],
        )

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(
            meeting_string, reply_markup=reply_markup, parse_mode="HTML"
        )

    async def cancel(self, update: Update, _context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text(
            "Создание встречи отменено.",
            reply_markup=ReplyKeyboardRemove(),
        )

        return ConversationHandler.END

    async def meeting_done(
        self, _update: Update, _context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        self.participants_state.reset()
        return ConversationHandler.END

    async def meeting_cancel(
        self, _update: Update, _context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        self.participants_state.reset()
        self.meeting.reset()
        return ConversationHandler.END

    async def start(self, update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
        keyboard = (
            [
                InlineKeyboardButton("Согласен", callback_data="accept_write_username"),
                InlineKeyboardButton(
                    "Отказываюсь", callback_data="reject_write_username"
                ),
            ],
        )

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "Привет! Я бот для встреч. Необходимо дать разрешение на запись твоего username в память",
            reply_markup=reply_markup,
        )
