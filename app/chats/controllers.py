"""All routes related to chats and actions to modify them"""
from flask import (jsonify, Blueprint, request)

from app.models import Chat, Participation, User
from app.chats.utils import chat_info, create_event
from app.auth.utils import requires_auth, user_is_logged_in
from playhouse.shortcuts import model_to_dict

chats = Blueprint('chats', __name__, url_prefix='/api/v1/chats')


@chats.route('/', methods=['GET'])
def list_all_chats():
    """Debug function to list the names of all chats"""
    # TODO: remove
    chats = [model_to_dict(chat) for chat in Chat.select()]
    return jsonify(chats), 200


@chats.route('/<chat_id>', methods=['GET'])
def get_chat_info(chat_id):
    chat = chat_info(chat_id)
    return jsonify(chat), 200


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


@chats.route('/<chat_id>', methods=['PATCH'])
@user_is_logged_in
def update_chat(chat_id):
    # TODO: Add check for participation
    data = request.get_json()
    chat_name = data.get("chat_name")
    theme = data.get("theme")

    chat = Chat.get(Chat.id == chat_id)
    if chat_name:
        chat.name = chat_name
    elif theme:
        chat.theme = theme

    if chat.save():
        return jsonify(model_to_dict(chat)), 200
    else:
        return "", 400


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
        "is_admin": either 0 for member or 1 for admin
    Client must include in the json one of either:
        "user_id": the id of the user
        "phone_number": the phone number of the user
    """
    # TODO: Add check for participation
    data = request.get_json()
    user_id = data.get("user_id")
    phone_number = data.get("phone_number")
    is_admin = data.get("is_admin")

    if is_admin is None or (user_id is None and phone_number is None):
        return str("Bad Data"), 400
    try:
        Participation.create(chat=chat_id, user=user_id, is_admin=is_admin)
    except Exception as e:
        return str(e), 400
    return "", 204


@chats.route('/<chat_id>/participants/<user_id>', methods=['PATCH'])
def update_participant(chat_id, user_id):
    data = request.get_json()
    is_admin = data.get("is_admin")

    try:
        query = Participation.update(is_admin=is_admin).where(
            Participation.chat == chat_id, Participation.user == user_id)
        query.execute()
        return "", 204
    except Exception as e:
        return str(e), 400


@chats.route('/<chat_id>/participants/<user_id>', methods=['DELETE'])
def delete_participant(chat_id, user_id):
    try:
        participant = Participation.get(Participation.chat == chat_id,
                                        Participation.user == user_id)
        if participant.delete_instance():
            return "", 204
        else:
            return "", 400
    except Exception as e:
        return str(e), 400


@chats.route('/<chat_id>/cursors/<user_id>', methods=['PATCH'])
def update_cursor(chat_id, user_id):
    data = request.get_json()

    cursor = data.get("cursor")

    participation = Participation.get(Participation.chat == chat_id,
                                      Participation.user == user_id)
    participation.cursor = cursor
    if participation.save():
        return "", 200
    else:
        return "", 400


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

    message_type = data.get("type")
    content = data.get("content")
    size = data.get("size")

    if message_type != "text" and message_type != "image":
        return str("Wrong type"), 400
    elif size < 0 or size > 1:
        return str("Bad size"), 400
    # TODO: if set to "image" test to make sure its a valid url

    result = create_event(
        chat_id,
        "message",
        1,  # TODO: Stop hardcoding the sender_id, and get the id using auth
        message_type=message_type,
        content=content,
        size=size)

    if result:
        return jsonify(result), 200
    else:
        return "", 400


"""
@chats.route('/<chat_id>/events/<event_index>', methods=['DELETE'])
def delete_message_from_chat(chat_id, event_index):
    try:
        events = Chat.get(Chat.id == chat_id).events
        del events[int(event_index)]
        query = Chat.update(events=events).where(Chat.id == chat_id)
        query.execute()
        # TODO: Update this using PostgreSQL json assessing features
        return "", 204
    except Exception as e:
        return str(e), 400
"""


@chats.route('/<chat_id>/likes', methods=['POST'])
def like_message(chat_id):
    # TODO: Add authentication allowing any member of the chat to use
    data = request.get_json()

    message_index = data.get("message_index")

    result = create_event(
        chat_id,
        "like",
        1,  # TODO: Stop hardcoding the sender_id, and get the id using auth
        message_index=message_index)

    if result:
        return jsonify(result), 200
    else:
        return "", 400


@chats.route('/<chat_id>/likes', methods=['DELETE'])
def unlike_message(chat_id):
    # TODO: Add authentication allowing any member of the chat to use
    data = request.get_json()

    message_index = data.get("message_index")

    result = create_event(
        chat_id,
        "dislike",
        1,  # TODO: Stop hardcoding the sender_id, and get the id using auth
        message_index=message_index)

    if result:
        return jsonify(result), 200
    else:
        return "", 400
