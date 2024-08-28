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

from constants import SELECT_APPROVE, SELECT_PARTICIPANTS_PREFIX, MEETING_READY
from meeting import Meeting
from commands import Commands
from listener import Listener
from participants import Participants
from config import BOT_TOKEN


def main() -> None:

    command_info = [
        ("start", "Знакомство с ботом, подтверждение регистрации"),
        ("create_meeting", "Создание встречи"),
    ]

    async def post_init(application: Application) -> None:
        await application.bot.set_my_commands(commands=command_info)

    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()

    participants_state = Participants()
    meeting = Meeting()
    commands = Commands(meeting, participants_state, app)
    listener = Listener(meeting, participants_state, app)
    participants_state.subscribe(
        lambda data: (
            meeting.add_participant(data)
            if data["status"] == SELECT_PARTICIPANTS_PREFIX
            else meeting.remove_participant(data)
        )
    )

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
                CallbackQueryHandler(
                    commands.meeting_done, pattern=f"^{MEETING_READY}$"
                ),
                CommandHandler("cancel", commands.cancel),
            ],
        ),
        CommandHandler("start", commands.start),
        CallbackQueryHandler(listener.button_listener),
    ]

    app.add_handlers(command_handlers)
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
