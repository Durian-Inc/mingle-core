"""All routes related to chats and actions to modify them"""
from flask import (jsonify, Blueprint, request, session)

from app.models import Chat, Participation, User
from app.chats.utils import chat_info
from app.auth.utils import requires_auth, user_is_logged_in
from playhouse.shortcuts import model_to_dict

chats = Blueprint('chats', __name__, url_prefix='/api/v1/chats')


@chats.route('/', methods=['GET'])
def list_all_chats():
    """Debug function to list the names of all chats"""
    # TODO: remove
    chats = [model_to_dict(chat) for chat in Chat.select()]
    return jsonify(chats), 200


@chats.route('/', methods=['POST'])
@user_is_logged_in
def create_chat():
    """
    Creates a chat specified by a client

    Client must post json including:
        "chat_name": name for the chat
        "users": a list of users to add on creation of the chat
    """
    data = request.get_json()
    chat_name = data.get("chat_name")

    try:
        new_chat = Chat.create(name=chat_name)
    except Exception as e:
        return str(e), 400
    if data.get("users") is not None:
        try:
            for phone_number in data.get("users"):
                user = User.select().where(
                    User.phone_number == phone_number).get()
                Participation.create(chat=new_chat, user=user, rank="member")
        except Exception as e:
            return str(e), 400

    return jsonify(model_to_dict(new_chat)), 201


@chats.route('/<chat_id>', methods=['GET'])
def get_chat_info(chat_id):
    chat = chat_info(chat_id)
    return jsonify(chat), 200


@chats.route('/<chat_id>', methods=['PATCH'])
@user_is_logged_in
def update_chat(chat_id):
    # TODO: Add check for participation
    data = request.get_json()
    chat_name = data.get("chat_name")

    chat = Chat.get(Chat.id == chat_id)
    query = Chat.update(name=chat_name).where(Chat.id == chat_id)
    query.execute()
    chat = Chat.get(Chat.id == chat_id)

    return jsonify(model_to_dict(chat)), 200


@chats.route('/<chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    try:
        chat = Chat.get(Chat.id == chat_id)
        query = Participation.delete().where(Participation.chat == chat)
        query.execute()
        if chat.delete_instance():
            return "", 204
        else:
            return "", 400
    except Exception as e:
        return str(e), 400


@chats.route('/<chat_id>/participants', methods=['POST'])
@user_is_logged_in
def add_user_to_chat(chat_id):
    """
    Adds a specified user to a chat identified by url "chat_id"

    Client must post json including:
        "rank": either 'member' or 'admin'
    Client must include in the json one of either:
        "user_id": the id of the user
        "phone_number": the phone number of the user
    """
    # TODO: Add check for participation
    data = request.get_json()
    user_id = data.get("user_id")
    phone_number = data.get("phone_number")
    rank = data.get("rank")

    if rank is None or (user_id is None and phone_number is None):
        return str("Bad Data"), 400
    try:
        Participation.create(chat=chat_id, user=user_id, rank=rank)
    except Exception as e:
        return str(e), 400
    return "", 204


@chats.route('/<chat_id>/participants/<user_id>', methods=['PATCH'])
def update_participant(chat_id, user_id):
    data = request.get_json()
    rank = data.get("rank")

    try:
        query = Participation.update(rank=rank).where(
            Participation.chat == chat_id and Participation.user == user_id)
        query.execute()
        return "", 204
    except Exception as e:
        return str(e), 400


@chats.route('/<chat_id>/participants/<user_id>', methods=['DELETE'])
def delete_participant(chat_id, user_id):
    try:
        query = Participation.delete().where(Participation.chat == chat_id
                                             and Participation.user == user_id)
        query.execute()
        return "", 204
    except Exception as e:
        return str(e), 400


@chats.route('/<chat_id>/messages', methods=['POST'])
@user_is_logged_in
def send_message_to_chat(chat_id):
    """
    Adds a specified message to a chat identified by url "chat_id"

    Client must post json including:
        "type": either 'text' or 'image'
        "content": corresponds to above, message or url
        "size": text only. 0.5 is normal size, spans from 0 to 1
    """
    # TODO: Add check for participation
    data = request.get_json()

    kind = data.get("type")
    message = data.get("content")
    size = data.get("size")
    if kind != "text" and kind != "image":
        return str("Wrong type"), 400
    elif size < 0 or size > 1:
        return str("Bad size"), 400
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

    return jsonify(chat), 200


@chats.route('/<chat_id>/messages/<message_index>', methods=['DELETE'])
def delete_message_from_chat(chat_id, message_index):
    try:
        chat = Chat.get(Chat.id == chat_id).messages
        del chat[int(message_index)]
        query = Chat.update(messages=chat).where(Chat.id == chat_id)
        query.execute()
        # TODO: Update this using PostgreSQL json assessing features
        return "", 204
    except Exception as e:
        return str(e), 400
