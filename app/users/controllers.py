from flask import (Blueprint, redirect, request, session, url_for)
from flask_cors import cross_origin

from app import CLIENT_ID
from app.models import AuthId, User, ChatMembership, Chat
from app.users.auth_utils import auth, jsonify, requires_auth
from json import dumps

users = Blueprint('users', __name__, url_prefix='/api/v1/users/')

@users.route('/', methods=['GET'])
def home():
    stuff = [x.name for x in User.select()]
    print(url_for('users.api_public'))
    return str(stuff)

@users.route('/callback', methods=['GET'])
def callback_handling():
    # Handles response from token endpoint to get the userinfo
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()

    # Store the user information in flask session.
    session['jwt_payload'] = userinfo
    session['profile'] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }

    user = User.create(
        display_name=userinfo['name'], photo_url=userinfo['picture'])
    AuthId.create(user=user, auth_id=userinfo['sub'])

    return redirect(url_for('users.user_info'), )

@users.route('/login', methods=['GET'])
def login():
    return auth0.authorize_redirect(
        redirect_uri='http://localhost:8080/api/v1/users/callback',
        audience='https://durian-inc.auth0.com/userinfo')


@users.route('/logout')
def logout():
    # Clear session stored data
    session.clear()
    # Redirect user to logout endpoint
    # TODO: Make this throw error message
    params = {
        'returnTo': url_for('users.home', _external=True),
        'client_id': CLIENT_ID
    }
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))


@users.route('/my_info', methods=['GET'])
@requires_auth
def user_info():
    return jsonify(session['jwt_payload'])


# needs auth later
@users.route('/<user_id>', methods=['POST'])
@requires_auth
def update(user_id):
    data = request.get_json()
    query = User.update(phone_number=data.get("phone_number")).where(
        User.user_id == user_id)
    query.execute()
    return "success"


@users.route('/<user_id>/chats', methods=['GET'])
def user_chats(user_id):
    # user = User.get(User.user_id == user_id)
    # return str(user.display_name)
    stuff = []
    res = ChatMembership.select().where(ChatMembership.user_id == user_id)
    for membership in res:
        thing = Chat.get(Chat.chat_id == membership.chat_id)
        stuff.append(thing.chat_blob)
    return jsonify(stuff)

@auth.route('/public', methods=['GET', 'POST'])
@cross_origin(headers=['Content-Type', 'Authorization'])
def api_public():
    # return(request.headers['Authorization'])
    # return(jsonify(dict(request.headers)))
    """
        Route that requires no authentication.
    """
    response = "No login necessary"
    return jsonify(message=response)

@auth.route('/private', methods=['GET', 'POST'])
@cross_origin(headers=['Content-Type', 'Authorization'])
@requires_auth
def api_private():
    """
        Route that requires authentication
    """
    response = "You are likely logged in so you good."
    return jsonify(message=response)
