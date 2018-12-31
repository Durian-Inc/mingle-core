"""Utility functions for using authentication"""
from functools import wraps
from flask_cors import cross_origin
import json
from werkzeug.exceptions import HTTPException

from flask import Blueprint, jsonify, redirect, session, url_for, _request_ctx_stack, request
from jose import jwt
from app.serve import CLIENT_ID, SECRET_KEY, app, API_AUDIENCE, AUTH0_DOMAIN, AUTHORIZE_URL, ACCESS_TOKEN_URL, REDIRECT_AUDIENCE, REDIRECT_URI
from authlib.flask.client import OAuth
from six.moves.urllib.request import urlopen
from six.moves.urllib.parse import urlencode

from app.users.utils import add_user

ALGORITHMS = ["RS256"]
auth = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id=CLIENT_ID,
    client_secret=SECRET_KEY,
    api_base_url=AUTH0_DOMAIN,
    access_token_url=ACCESS_TOKEN_URL,
    authorize_url=AUTHORIZE_URL,
    client_kwargs={
        'scope': 'openid profile',
    },
)


def requires_auth(func):
    """Decorator to specify that function needs to be authenticated"""

    @wraps(func)
    def decorated(*args, **kwargs):
        """Check authentication, or get failure"""
        if 'profile' not in session:
            # Redirect to Login page here
            return jsonify(success=False, error="Authentication failure")
        else:
            if 'token' not in session:
                return jsonify(success=False, error="Token is not in session")
            else:
                token = session['token']
                jsonurl = urlopen(AUTH0_DOMAIN + "/.well-known/jwks.json")
                jwks = json.loads(jsonurl.read())
                unverified_header = jwt.get_unverified_header(token)
                rsa_key = {}
                for key in jwks["keys"]:
                    if key["kid"] == unverified_header["kid"]:
                        rsa_key = {
                            "kty": key["kty"],
                            "kid": key["kid"],
                            "use": key["use"],
                            "n": key["n"],
                            "e": key["e"]
                        }
                if rsa_key:
                    try:
                        payload = jwt.decode(
                            token,
                            rsa_key,
                            algorithms=ALGORITHMS,
                            audience=CLIENT_ID,
                            issuer=AUTH0_DOMAIN + "/")
                    except jwt.ExpiredSignatureError:
                        raise AuthError({
                            "code": "token_expired",
                            "description": "token is expired"
                        }, 401)
                    except jwt.JWTClaimsError:
                        raise AuthError({
                            "code":
                            "invalid_claims",
                            "description":
                            "incorrect claims,"
                            "please check the audience and issuer"
                        }, 401)
                    except Exception:
                        raise AuthError(
                            {
                                "code": "invalid_header",
                                "description": "Unable to parse authentication"
                                " token."
                            }, 401)
        return func(*args, **kwargs)

    return decorated


# Error handler
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


def requires_scope(required_scope):
    """Determines if the required scope is present in the Access Token
    Args:
        required_scope (str): The scope required to access the resource
    """
    token = session['token']
    unverified_claims = jwt.get_unverified_claims(token)
    if unverified_claims.get("scope"):
        token_scopes = unverified_claims["scope"].split()
        for token_scope in token_scopes:
            if token_scope == required_scope:
                return True
    return False


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
@cross_origin(headers=['Content-Type', 'Authorization'])
def api_public():
    """
        Route that requires no authentication.
    """
    return jsonify(message="Public route with no auth")


@auth.route('/private', methods=['GET', 'POST'])
@cross_origin(headers=['Content-Type', 'Authorization'])
@requires_auth
def api_private():
    """
        Route that requires authentication
    """
    return jsonify(message="Private route with auth")