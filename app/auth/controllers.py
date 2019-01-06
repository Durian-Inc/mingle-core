"""All routes related to authentication"""
from flask import jsonify, Blueprint, redirect, url_for
from flask_cors import cross_origin

from app.auth.utils import auth0, requires_auth
from app.serve import CLIENT_ID, REDIRECT_AUDIENCE, REDIRECT_URI
from six.moves.urllib.parse import urlencode

from app.users.utils import add_user
from app.users.controllers import users
from app.models import User

auth = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@auth.route('/callback', methods=['GET'])
def callback_handling():
    """Handles response from token endpoint to get the userinfo"""
    token = auth0.authorize_access_token()
    # TODO: Send the token back to the client
    resp = auth0.get('userinfo')
    userinfo = resp.json()
    res = add_user(userinfo['name'], userinfo['picture'], userinfo['sub'])
    if res:
        return jsonify(success=False, error=res)
    return redirect(url_for('users.user_info', user_id=User.select().count()))


@auth.route('/login', methods=['GET'])
def login():
    """Access the login page"""
    return auth0.authorize_redirect(
        redirect_uri=REDIRECT_URI,
        audience=REDIRECT_AUDIENCE)


@auth.route('/logout', methods=['GET'])
@cross_origin(headers=['Content-Type', 'Authorization'])
@requires_auth
def logout():
    """Removes token from the client's side to log them out of the system"""
    # TODO: Remove token from client
    # Redirect user to logout endpoint
    params = {
        'returnTo': url_for('auth.api_public', _external=True),
        'client_id': CLIENT_ID
    }
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

# Routes used for debugging
@auth.route('/public', methods=['GET', 'POST'])
def api_public():
    """
        Route that requires no authentication.
    """
    return jsonify(message="Public route with no auth")

# Routes using authentication should implement cross_origin and call the requires_auth decorator
@auth.route('/private', methods=['GET', 'POST'])
@cross_origin(headers=['Content-Type', 'Authorization'])
@requires_auth
def api_private():
    """Route that requires authentication."""
    return jsonify(message="Private route with auth")