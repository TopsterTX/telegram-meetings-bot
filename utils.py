from telegram import InlineKeyboardButton
from math import floor, ceil

from constants import SELECT_PARTICIPANTS_PREFIX, PARTICIPANT_OFFSET, SELECT_APPROVE


def generate_participants():
    file = open("./list.txt", "r")
    content = file.read()
    participants = content.split("\n")
    participants_len = len(participants)

    result = []

    if participants_len:
        for participant in participants:
            if participant != "":
                username, chat_id = participant.split(" ")
                result.append((username, chat_id))

    file.close()
    return result


def sort(participants):
    is_sorted = len(participants) > PARTICIPANT_OFFSET

    arr = (
        [[] for _ in range(ceil(len(participants) / PARTICIPANT_OFFSET))]
        if is_sorted
        else [[]]
    )

    for ind, user in enumerate(participants):
        arr[floor(ind / PARTICIPANT_OFFSET) if is_sorted else 0].append(user)

    return arr


def generate_participants_keyboard(admin: str, participants):
    keyboard = []

    for ind, username in enumerate(participants):
        if username != admin:
            is_selected = participants[username]["status"] == SELECT_PARTICIPANTS_PREFIX
            button_title = f"{username} 👍" if is_selected else username
            keyboard.append(
                [
                    InlineKeyboardButton(
                        button_title,
                        callback_data=f"{participants[username]['status']} {username}",
                    )
                ]
            )

    keyboard.append([InlineKeyboardButton("Готово", callback_data=SELECT_APPROVE)])

    return keyboard


def add_participant(username: str, chat_id: int):
    file = open("./list.txt", "a")
    file.write(f"{username} {chat_id}" + "\n")
    file.close()


def generate_meeting_string(admin_username: str, theme: str, date: str, participants):
    participants_string = ""
    for ind, participant in enumerate(participants):
        participants_string += (
            ", " if ind != 0 else ""
        ) + f"@{participant['username']}"

    text = f"Создатель встречи: @{admin_username}\n\n<b>{theme}</b>\nДата: {date}\nУчастники: {participants_string}"

    return text
