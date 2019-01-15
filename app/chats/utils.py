from app.models import Chat, Participation
from datetime import datetime

from playhouse.shortcuts import model_to_dict


def chat_info(chat_id):
    chat = Chat.get(Chat.id == chat_id)
    users = [
        model_to_dict(x.user)
        for x in Participation.select().where(Participation.chat == chat_id)
    ]
    return dict(chat=model_to_dict(chat), users=users)


def create_event(chat_id, event_type, sender, **kwargs):
    event = {
        "event": event_type,
        "sender": sender,
        "timestamp": datetime.now().isoformat(),
        "payload": kwargs
    }
    chat = Chat.get(Chat.id == chat_id)
    chat.events.append(event)
    # TODO: Update this using PostgreSQL json features
    if chat.save():
        return chat
    else:
        return None
