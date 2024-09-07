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
    MEETING_READY,
    MEETING_CANCEL,
    START,
    LIST_FRIENDS,
    CREATE_MEETING,
    SELECT_PARTICIPANTS_PREFIX,
    UNSELECT_PARTICIPANTS_PREFIX,
    NOTIFY_PREFIX,
    SUCCESS_REGISTRATION,
    REJECT_REGISTRATION,
)
from config import BOT_TOKEN, DB_NAME, DB_HOST, DB_PASS, DB_PORT, DB_USER
from meeting import Meeting
from user import User
from commands import Commands
from db import Db


def main() -> None:

    command_info = [
        (START, "Знакомство с ботом, подтверждение регистрации"),
        (LIST_FRIENDS, "Список зарегистрированных пользователей"),
        (CREATE_MEETING, "Создание встречи"),
    ]

    async def post_init(application: Application) -> None:
        await application.bot.set_my_commands(commands=command_info)

    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()

    db = Db(dbname=DB_NAME, host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS)

    user = User(db)
    meeting = Meeting(db)
    commands = Commands(app, db, user, meeting)

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
                # CallbackQueryHandler(
                #     commands.select_participants,
                #     pattern=f"^{SELECT_PARTICIPANTS_PREFIX}|^{UNSELECT_PARTICIPANTS_PREFIX}",
                # ),
                # CallbackQueryHandler(
                #     commands.meeting_done,
                #     pattern=f"^{MEETING_READY}$",
                # ),
                # CallbackQueryHandler(
                #     commands.registration_buttons_listener,
                #     pattern=f"r'(^{SUCCESS_REGISTRATION}|^{REJECT_REGISTRATION})$",
                # ),
                # CallbackQueryHandler(commands.cancel, pattern=f"^{MEETING_CANCEL}$"),
                # CallbackQueryHandler(commands.default_button_listener),
                CommandHandler("cancel", commands.cancel),
            ],
        ),
        CommandHandler("start", commands.start),
        CommandHandler("list_friends", commands.list_friends),
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
