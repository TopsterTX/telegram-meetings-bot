from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from constants import (
    SELECT_APPROVE,
    START,
    LIST_USERS,
    CREATE_MEETING,
    NOTIFY_PREFIX,
    SUCCESS_REGISTRATION,
    REJECT_REGISTRATION,
)
from config import BOT_TOKEN
from event_emmiter import EventEmitter
from handlers import register_event_emitter_handlers
from meeting import Meeting
from user import User
from commands import Commands
from db import Db


def main() -> None:

    command_info = [
        (START, "Регистрация"),
        (LIST_USERS, "Список зарегистрированных пользователей"),
        (CREATE_MEETING, "Создание встречи"),
    ]

    async def post_init(application: Application) -> None:
        await application.bot.set_my_commands(commands=command_info)

    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()
    event_emitter = EventEmitter()
    db = Db()

    user = User(db)
    meeting = Meeting(db)
    commands = Commands(app, db, user, meeting, event_emitter)

    # Register handlers
    register_event_emitter_handlers(event_emitter)

    command_handlers = [
        ConversationHandler(
            entry_points=[CommandHandler("create_meeting", commands.create_meeting)],
            states={
                commands.THEME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, commands.get_theme)
                ],
                commands.DATE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, commands.get_date)
                ],
                commands.PARTICIPANTS: [
                    CallbackQueryHandler(
                        commands.get_participants_and_apply,
                        pattern=f"^{SELECT_APPROVE}$",
                    ),
                ],
            },
            fallbacks=[
                CallbackQueryHandler(commands.button_listener),
                CommandHandler("cancel", commands.cancel),
            ],
        ),
        CommandHandler("start", commands.start),
        CommandHandler("list_users", commands.list_users),
        CallbackQueryHandler(
            commands.registration_buttons_listener,
            pattern=f"(^{SUCCESS_REGISTRATION}|^{REJECT_REGISTRATION})$",
        ),
        CallbackQueryHandler(commands.answer_users, pattern=f"^{NOTIFY_PREFIX}"),
    ]

    app.add_handlers(command_handlers)
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
