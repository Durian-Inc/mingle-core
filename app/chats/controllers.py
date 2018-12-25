from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)

from app import CLIENT_ID, SECRET_KEY
from app.models import AuthId, User, Chat, ChatMembership

chats = Blueprint('chats', __name__, url_prefix='/api/v1/chats')


@chats.route('/', methods=['GET'])
def home():
    stuff = [x.name for x in Chat.select()]
    return str(stuff)


@chats.route('/', methods=['POST'])
def create_chat():
    data = request.get_json()
    chat_name = data.get("chat_name")
    new_chat = Chat.create(name=chat_name)
    for number in data.get("users"):
        pass
    return "nice"


@chats.route('/<chat_id>', methods=['POST'])
def add_user_to_chat(chat_id):
    data = request.get_json()
    user_id = data.get("user_id")
    # rank = data.get("rank")
    ChatMembership.create(chat_id=chat_id, user_id=user_id)
    return "nice!"
