from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler, Application
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
    CallbackQuery,
)

from constants import (
    MEETING_CANCEL,
    MEETING_READY,
    REJECT_REGISTRATION,
    SUCCESS_REGISTRATION,
    START,
    CANCEL_COMMAND,
    SELECT_PARTICIPANTS_PREFIX,
    UNSELECT_PARTICIPANTS_PREFIX,
    NOTIFY_PREFIX,
    NOTIFY_REJECT,
    NOTIFY_ACCEPT,
    NOTIFY_LATE,
    PROCESSING,
    RECORD_ALREADY_EXIST,
    DEFAULT_ERROR,
    CREATE_MEETING,
    CANCEL_MEETING_TEXT,
    CHECK_MEETING_PARTICIPANTS,
)
from event_emmiter import EventEmitter
from user import User
from meeting import Meeting
from db import Db
from utils import (
    generate_participants_keyboard,
    generate_meeting_string,
)


class Commands:
    def __init__(
        self,
        app: Application,
        db: Db,
        user: User,
        meeting: Meeting,
        event_emitter: EventEmitter,
    ):
        self.current_meeting_id = ""
        self.db = db
        self.app = app
        self.user = user
        self.meeting = meeting
        self.event_emitter = event_emitter
        self.THEME, self.DATE, self.PARTICIPANTS = range(0, 3)

    async def list_users(self, update: Update, _context: ContextTypes.DEFAULT_TYPE):
        participants_data = self.user.get_users()
        participants_text = ""

        for user in participants_data:
            _id, username, _chat_id, first_name = user
            participants_text += f"@<b>{username}</b>: {first_name}\n"

        if participants_text:
            await update.message.reply_text(
                participants_text, parse_mode=ParseMode.HTML
            )
        else:
            await update.message.reply_text(
                f"Список пуст.\nЗарегистрируйтесь, использую команду /{START}"
            )

    async def create_meeting(
        self, update: Update, _context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        users_from_db = self.user.get_users()
        user_from_db = self.user.get_user_by_chat_id(update.message.chat.id)

        if not user_from_db:
            await update.message.reply_text(
                f"Вам необходимо зарегистрироваться !\nВыполните команду /{START}"
            )
            return ConversationHandler.END
        elif len(users_from_db) <= 1:
            await update.message.reply_text(
                f"Список зарегистированных пользователей пуст.\nВы не сможете добавить участников встречи."
            )
        else:
            (id, username, *_rest) = user_from_db
            self.current_meeting_id = self.meeting.create_meeting()
            self.meeting.set_meeting_data(
                self.current_meeting_id,
                (("admin_user_id", id),),
            )

            await update.message.reply_text(
                f"Создание встречи можно прервать в любой момент, используя команду /{CANCEL_COMMAND}"
            )
            await update.message.reply_text(f"Админ: {username}\nУкажите тему встречи:")

            return self.THEME

    async def get_theme(
        self, update: Update, _context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        theme = update.message.text
        self.meeting.set_meeting_data(self.current_meeting_id, (("theme", theme),))

        await update.message.reply_text("Укажите дату встречи (dd.mm.yyyy hh:mm):")

        return self.DATE

    async def get_date(
        self, update: Update, _context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        date = update.message.text
        self.meeting.set_meeting_data(self.current_meeting_id, (("date", date),))

        keyboard = generate_participants_keyboard(
            self.meeting, self.user, self.current_meeting_id
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

        (_id, theme, status, admin_user_id, date) = self.meeting.get_meeting_by_id(
            self.current_meeting_id
        )
        (_id, admin_username, *_rest) = self.user.get_user_by_id(admin_user_id)
        selected_participants = self.meeting.get_meeting_participants(
            self.current_meeting_id, ("username",)
        )

        meeting_string = generate_meeting_string(
            theme,
            date,
            selected_participants,
            admin_username,
        )
        keyboard = (
            [
                InlineKeyboardButton("Готово", callback_data=MEETING_READY),
                InlineKeyboardButton("Отмена", callback_data=MEETING_CANCEL),
            ],
        )

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(
            meeting_string, reply_markup=reply_markup, parse_mode=ParseMode.HTML
        )

    async def select_participants(self, query: CallbackQuery):
        status, username = query.data.split(" ")
        (user_id, *_rest) = self.user.get_user_by_username(username)

        if status == SELECT_PARTICIPANTS_PREFIX:
            self.meeting.add_participant_to_meeting(self.current_meeting_id, user_id)
        elif status == UNSELECT_PARTICIPANTS_PREFIX:
            self.meeting.remove_participant_to_meeting(self.current_meeting_id, user_id)

        keyboard = generate_participants_keyboard(
            self.meeting, self.user, self.current_meeting_id
        )
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_reply_markup(reply_markup=reply_markup)

    async def button_listener(
        self, update: Update, _context: ContextTypes.DEFAULT_TYPE
    ) -> int or None:

        message = update.message
        query = update.callback_query

        await query.answer()

        if query.data.startswith(SELECT_PARTICIPANTS_PREFIX) or query.data.startswith(
            UNSELECT_PARTICIPANTS_PREFIX
        ):
            await self.select_participants(query)

        if query.data == MEETING_READY:
            await self.meeting_done(query)

            return ConversationHandler.END

        if query.data == MEETING_CANCEL:
            self.meeting.set_status(self.current_meeting_id, CANCEL_COMMAND)
            self.current_meeting_id = None
            await query.edit_message_text(CANCEL_MEETING_TEXT)

            return ConversationHandler.END

    async def cancel(self, update: Update, _context: ContextTypes.DEFAULT_TYPE) -> int:
        self.meeting.set_status(self.current_meeting_id, CANCEL_COMMAND)
        self.current_meeting_id = None
        await update.message.reply_text(
            CANCEL_MEETING_TEXT,
            reply_markup=ReplyKeyboardRemove(),
        )

        return ConversationHandler.END

    async def meeting_done(self, query: CallbackQuery) -> int:

        self.meeting.set_status(self.current_meeting_id, PROCESSING)
        (_id, theme, status, admin_user_id, date) = self.meeting.get_meeting_by_id(
            self.current_meeting_id
        )
        # (_id, admin_username, *_rest) = self.user.get_user_by_id(admin_user_id)
        selected_participants = self.meeting.get_meeting_participants(
            self.current_meeting_id,
            ("username", "chat_id"),
        )
        meeting_string = generate_meeting_string(
            theme,
            date,
            selected_participants,
        )

        for participant in selected_participants:
            (username, chat_id) = participant

            callback_data_accept = f"{NOTIFY_PREFIX} {username} {NOTIFY_ACCEPT}"
            callback_data_late = f"{NOTIFY_PREFIX} {username} {NOTIFY_LATE}"
            callback_data_reject = f"{NOTIFY_PREFIX} {username} {NOTIFY_REJECT}"

            keyboard = (
                [
                    InlineKeyboardButton(
                        "Принять", callback_data=f"{callback_data_accept}"
                    ),
                    InlineKeyboardButton(
                        "Опоздаю", callback_data=f"{callback_data_late}"
                    ),
                    InlineKeyboardButton(
                        "Отклонить", callback_data=f"{callback_data_reject}"
                    ),
                ],
            )

            reply_markup = InlineKeyboardMarkup(keyboard)

            await self.app.bot.send_message(
                chat_id=chat_id,
                text=meeting_string,
                reply_markup=reply_markup,
                parse_mode="HTML",
            )

        await query.edit_message_text(text="Встреча создана")

        return ConversationHandler.END

    async def answer_users(
        self, update: Update, _context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        query = update.callback_query

        await query.answer()

        _, username, status = query.data.split(" ")
        (user_id, *_rest) = self.user.get_user_by_username(username)
        (_id, theme, _status, admin_user_id, *_rest) = self.meeting.get_meeting_by_id(
            self.current_meeting_id
        )
        (_id, _username, admin_chat_id, *_rest) = self.user.get_user_by_id(
            admin_user_id
        )

        if status == NOTIFY_ACCEPT:
            await self.app.bot.send_message(
                chat_id=admin_chat_id,
                text=f"@{username} принял встречу:\n<b>{theme}</b>",
                parse_mode=ParseMode.HTML,
            )

        if status == NOTIFY_LATE:
            await self.app.bot.send_message(
                chat_id=admin_chat_id,
                text=f"@{username} опоздает на встречу:\n<b>{theme}</b>",
                parse_mode=ParseMode.HTML,
            )

        if status == NOTIFY_REJECT:
            self.meeting.remove_participant_to_meeting(self.current_meeting_id, user_id)
            self.event_emitter.emit(
                CHECK_MEETING_PARTICIPANTS,
                self.meeting,
                self.current_meeting_id,
            )
            await self.app.bot.send_message(
                chat_id=admin_chat_id,
                text=f"@{username} отказался от встречи:\n<b>{theme}</b>",
                parse_mode=ParseMode.HTML,
            )

        await query.edit_message_text("Отлично, уведомил администратора")

    async def registration_buttons_listener(
        self, update: Update, _context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        query = update.callback_query
        await query.answer()

        user = query.from_user
        message = query.message

        if query.data == SUCCESS_REGISTRATION:
            try:
                self.user.create_user(
                    ("username", "chat_id", "first_name"),
                    (user.username, message.chat.id, user.first_name),
                )
                await query.edit_message_text(
                    f"Готово, теперь вы можете создавать встречи\nДля этого воспользуйся командой /{CREATE_MEETING}"
                )
            except Exception as e:
                print(e)
                if e.args.__contains__(RECORD_ALREADY_EXIST):
                    await query.edit_message_text("Ты уже зарегистрирован")
                if e.args.__contains__(DEFAULT_ERROR):
                    await query.edit_message_text(
                        "Произошла ошибка, обратитись к администратору"
                    )

        if query.data == REJECT_REGISTRATION:
            await query.edit_message_text("Нет, ну так не пойдёт")

    async def start(self, update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
        keyboard = (
            [
                InlineKeyboardButton(
                    "Зарегистрируй меня", callback_data=SUCCESS_REGISTRATION
                ),
                InlineKeyboardButton("Отказываюсь", callback_data=REJECT_REGISTRATION),
            ],
        )

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "Привет! Я бот для встреч. Для создания встреч необходимо зарегистрироваться.",
            reply_markup=reply_markup,
        )
