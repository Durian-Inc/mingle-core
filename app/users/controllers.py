"""Interactions with users happen on these routes"""
from flask import Blueprint, redirect, request, session, url_for

from six.moves.urllib.parse import urlencode

from app.serve import CLIENT_ID
from app.models import AuthId, User, Participation, Chat
from app.auth_utils import auth0, jsonify, requires_auth

users = Blueprint('users', __name__, url_prefix='/api/v1/users/')


@users.route('/', methods=['GET'])
def list_users():
    """Debug function to list all users in the database"""
    # TODO: remove
    names = [x.display_name for x in User.select()]
    return jsonify(names)


@users.route('/callback', methods=['GET'])
def callback_handling():
    """Handles response from token endpoint to get the userinfo"""
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

    return redirect(url_for('users.user_info'))


@users.route('/login', methods=['GET'])
def login():
    """Access the login page"""
    return auth0.authorize_redirect(
        redirect_uri='http://localhost:8080/api/v1/users/callback',
        audience='https://durian-inc.auth0.com/userinfo')


@users.route('/logout', methods=['GET'])
def logout():
    """Removes user login details from session, logging out the user"""
    session.clear()
    # TODO: Make clear only significant session storage
    # TODO: Handle error messages and auth for this function
    # Redirect user to logout endpoint
    params = {
        'returnTo': url_for('users.home', _external=True),
        'client_id': CLIENT_ID
    }
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))


@users.route('/my_info', methods=['GET'])
@requires_auth
def user_info():
    """Spits out all session information about user"""
    # TODO: remove
    return jsonify(session['jwt_payload'])


@users.route('/<user_id>', methods=['PATCH'])
def update(user_id):
    """
    Changes information about user specified by id in the url
    """
    # TODO: add auth that only allows this user id to access
    data = request.get_json()
    phone_number = data.get("phone_number")
    display_name = data.get("display_name")
    if phone_number is None and display_name is None:
        return jsonify(success=True)
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
    return jsonify(success=True)


@users.route('/<user_id>/chats', methods=['GET'])
def user_chats(user_id):
    """List all chats for a given user"""
    chats = []
    raw_chats = Participation.select().where(Participation.user == user_id)
    for item in raw_chats:
        chat = Chat.get(Chat.id == item.chat)
        chats.append(chat.messages)
    return jsonify(chats)
