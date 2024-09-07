from telegram import InlineKeyboardButton

from constants import (
    SELECT_PARTICIPANTS_PREFIX,
    SELECT_APPROVE,
    UNSELECT_PARTICIPANTS_PREFIX,
)
from meeting import Meeting
from user import User


def generate_participants_keyboard(meeting: Meeting, user: User, current_meeting_id):
    (_id, _theme, _status, admin_user_id, *_rest) = meeting.get_meeting_by_id(
        current_meeting_id
    )
    selected_users_id = meeting.get_meeting_participants(
        current_meeting_id, ("user_id",)
    )

    # (("id", "!=", admin_user_id),)
    participants = user.get_users()

    keyboard = []

    for ind, participant in enumerate(participants):
        user_id, username, _chat_id, first_name = participant

        is_selected = (user_id,) in selected_users_id
        button_title = (
            f"{username} {first_name} 👍" if is_selected else f"{username} {first_name}"
        )
        callback_data_prefix = (
            UNSELECT_PARTICIPANTS_PREFIX if is_selected else SELECT_PARTICIPANTS_PREFIX
        )
        keyboard.append(
            [
                InlineKeyboardButton(
                    button_title,
                    callback_data=f"{callback_data_prefix} {username}",
                )
            ]
        )

    keyboard.append([InlineKeyboardButton("Готово", callback_data=SELECT_APPROVE)])

    return keyboard


def add_participant(username: str, chat_id: int):
    file = open("./list.txt", "a")
    file.write(f"{username} {chat_id}" + "\n")
    file.close()


def generate_meeting_string(
    theme: str, date: str, participants, admin_username: str = None
):
    participants_string = ""
    for ind, participant_data in enumerate(participants):
        (username, *_rest) = participant_data
        participants_string += (", " if ind != 0 else "") + f"@{username}"

    admin_title = f"Создатель встречи: @{admin_username}" if admin_username else ""

    text = f"{admin_title}\n\n<b>{theme}</b>\nДата: {date}\nУчастники: {participants_string}"

    return text
