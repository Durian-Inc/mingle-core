from app.models import Chat, Participation

from playhouse.shortcuts import model_to_dict


def chat_info(chat_id):
    chat = Chat.get(Chat.id == chat_id)
    users = [
        model_to_dict(x.user)
        for x in Participation.select().where(Participation.chat == chat_id)
    ]
    return dict(chat=model_to_dict(chat), users=users)
