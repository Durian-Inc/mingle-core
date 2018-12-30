"""All routes related to chats and actions to modify them"""
from flask import (jsonify, Blueprint, request)

from app.models import Chat, Participation
from playhouse.shortcuts import model_to_dict

chats = Blueprint('chats', __name__, url_prefix='/api/v1/chats')


@chats.route('/', methods=['GET'])
def list_all_chats():
    """Debug function to list the names of all chats"""
    # TODO: remove
    names = [{x.id: x.name} for x in Chat.select()]
    return jsonify(names)


@chats.route('/', methods=['POST'])
def create_chat():
    """
    Creates a chat specified by a client

    Client must post json including:
        "chat_name": name for the chat
        "users": a list of users to add on creation of the chat
    """
    # TODO: Add authentication allowing any logged in user to use
    data = request.get_json()
    chat_name = data.get("chat_name")
    try:
        Chat.create(name=chat_name)
    except Exception as e:
        return jsonify(success=False, error=str(e))
    # TODO: Create Participation for each user specified
    # When implemented use: new_chat = Chat.create(name=chat_name)
    # for number in data.get("users"):
    # pass
    return jsonify(success=True)


@chats.route('/<chat_id>', methods=['GET'])
def get_chat_info(chat_id):
    chat = Chat.get(Chat.id == chat_id)
    users = [{
        x.user.id: x.user.display_name
    } for x in Participation.select().where(Participation.chat == chat_id)]
    return jsonify(chat=model_to_dict(chat), users=users)


@chats.route('/<chat_id>', methods=['PATCH'])
def add_user_to_chat(chat_id):
    """
    Adds a specified user to a chat identified by url "chat_id"

    Client must post json including:
        "rank": either 'member' or 'admin'
    Client must include in the json one of either:
        "user_id": the id of the user
        "phone_number": the phone number of the user
    """
    # TODO: Add authentication allowing any member of the chat to use
    data = request.get_json()
    user_id = data.get("user_id")
    phone_number = data.get("phone_number")
    rank = data.get("rank")
    if rank is None or (user_id is None and phone_number is None):
        return jsonify(success=False, error="Bad data")
    try:
        # TODO: Should it be querying for the chat and user
        Participation.create(chat=chat_id, user=user_id, rank=rank)
    except Exception as e:
        return jsonify(success=False, error=str(e))
    return jsonify(success=True)


@chats.route('/<chat_id>/messages', methods=['POST'])
def send_message_to_chat(chat_id):
    """
    Adds a specified message to a chat identified by url "chat_id"

    Client must post json including:
        "type": either 'text' or 'image'
        "content": corresponds to above, message or url
        "size": text only. 0.5 is normal size, spans from 0 to 1
    """
    # TODO: Add authentication allowing any member of the chat to use
    data = request.get_json()

    kind = data.get("type")
    message = data.get("content")
    size = data.get("size")
    if kind != "text" and kind != "image":
        return jsonify(success=False, error="Wrong type")
    elif size < 0 or size > 1:
        return jsonify(success=False, error="Bad size")
    # TODO: if set to "image" test to make sure its a valid url

    data = {
        "sender_id": 1,
        "type": kind,
        "content": message,
        "size": size,
        "seen_by": []
    }
    # TODO: Stop hardcoding the sender_id, and get the id using auth
    chat = Chat.get(Chat.id == chat_id).messages
    chat.append(data)
    query = Chat.update(messages=chat).where(Chat.id == chat_id)
    query.execute()
    # TODO: Update this using PostgreSQL json assessing features

    return jsonify(success=True)
