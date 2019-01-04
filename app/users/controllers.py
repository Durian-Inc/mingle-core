"""Interactions with users happen on these routes"""
from flask import Blueprint, jsonify, request, session

from app.models import Chat, Participation, User

from playhouse.shortcuts import model_to_dict

users = Blueprint('users', __name__, url_prefix='/api/v1/users/')


@users.route('/', methods=['GET'])
def list_all_users():
    """Lists all users"""
    # TODO: remove
    names = [{x.id: x.display_name} for x in User.select()]
    return jsonify(names), 200


@users.route('/<user_id>', methods=['GET'])
def user_info(user_id):
    """Spits out all session information about user"""
    user = User.get(User.id == user_id)
    return jsonify(model_to_dict(user)), 200


@users.route('/<user_id>', methods=['PATCH'])
def update_user(user_id):
    """Changes information about user specified by id in the url"""
    # TODO: add auth that only allows this user id to access
    data = request.get_json()
    phone_number = data.get("phone_number")
    display_name = data.get("display_name")

    if phone_number is None and display_name is None:
        return "", 204
    elif phone_number is not None and display_name is None:
        query = User.update(phone_number=phone_number).where(
            User.id == user_id)
        query.execute()
    elif phone_number is None and display_name is not None:
        query = User.update(display_name=display_name).where(
            User.id == user_id)
        query.execute()
    elif phone_number is not None and display_name is not None:
        query = User.update(
            display_name=display_name,
            phone_number=phone_number).where(User.id == user_id)
        query.execute()
    # TODO: Some error checking
    return "", 204


@users.route('/<user_id>/chats', methods=['GET'])
def list_user_chats(user_id):
    """List all chats for a given user"""
    chats = []
    raw_chats = Participation.select().where(Participation.user == user_id)
    for item in raw_chats:
        chat = Chat.get(Chat.id == item.chat)
        chats.append(model_to_dict(chat))
    return jsonify(chats), 200
