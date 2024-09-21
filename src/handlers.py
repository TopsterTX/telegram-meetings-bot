from constants import CHECK_MEETING_PARTICIPANTS, REJECT
from event_emmiter import EventEmitter
from meeting import Meeting


def register_event_emitter_handlers(event_emitter: EventEmitter):
    def check_meeting_participants(meeting: Meeting, meeting_id: str):
        participants = meeting.get_meeting_participants(meeting_id)
        if len(participants) <= 0:
            meeting.set_status(meeting_id, REJECT)

    event_emitter.on(CHECK_MEETING_PARTICIPANTS, check_meeting_participants)
