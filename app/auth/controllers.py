from flask import jsonify, session, Blueprint, redirect
from app.utils import auth0 
from app.serve import CLIENT_ID, REDIRECT_AUDIENCE, REDIRECT_URI

from app.users.utils import add_user

auth = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@auth.route('/callback', methods=['GET'])
def callback_handling():
    """Handles response from token endpoint to get the userinfo"""
    token = auth0.authorize_access_token()
    session['token'] = token['id_token']
    resp = auth0.get('userinfo')
    userinfo = resp.json()

    # Store the user information in flask session.
    session['jwt_payload'] = userinfo
    session['profile'] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }

    res = add_user(userinfo['name'], userinfo['picture'], userinfo['sub'])
    if res:
        return jsonify(success=False, error=res)
    return redirect(url_for('users.user_info'))


@auth.route('/login', methods=['GET'])
def login():
    """Access the login page"""
    return auth0.authorize_redirect(
        redirect_uri=REDIRECT_URI,
        audience=REDIRECT_AUDIENCE)


@auth.route('/logout', methods=['GET'])
def logout():
    """Removes user login details from session, logging out the user"""
    session.clear()
    # TODO: Make clear only significant session storage
    # TODO: Handle error messages and auth for this function
    # Redirect user to logout endpoint
    params = {
        'returnTo': url_for('auth.api_public', _external=True),
        'client_id': CLIENT_ID
    }
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

@auth.route('/public', methods=['GET', 'POST'])
def api_public():
    """
        Route that requires no authentication.
    """
    return jsonify(message="Public route with no auth")


@auth.route('/private', methods=['GET', 'POST'])
@requires_auth
def api_private():
    """
        Route that requires authentication
    """
    return jsonify(message="Private route with auth")