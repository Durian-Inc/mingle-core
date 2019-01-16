"""Utility functions for using authentication"""
import json
from functools import wraps
from urllib.parse import urljoin

import requests
from flask import jsonify, session

from app.serve import (ACCESS_TOKEN_URL, AUTH0_DOMAIN, AUTHORIZE_URL,
                       CLIENT_ID, SECRET_KEY, app)
from authlib.flask.client import OAuth
from jose import jwt

ALGORITHMS = ["RS256"]
KEYS_TO_CLEAR = ['profile', 'jwt_payload', 'token', 'token_sub']

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


# Auth Error handler
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
                jsonurl = requests.get(
                    urljoin("https://", AUTH0_DOMAIN, ".well-known/jwks.json"))
                jwks = jsonurl.json()
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
                        session['token_sub'] = payload['sub']
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
                        raise AuthError({
                            "code":
                            "invalid_header",
                            "description":
                            "Unable to parse authentication"
                            " token."
                        }, 401)
        return func(*args, **kwargs)

    return decorated


def user_is_logged_in(func):
    """Validate that the user's sub is the same as the token's"""

    @wraps(func)
    def decorated(*args, **kwargs):
        try:
            profile_sub = session['profile']['user_id']
            token_sub = session['token_sub']
            if token_sub != profile_sub:
                raise AuthError(
                    {
                        "code": "invalid_user",
                        "description": "User is not logged in with token"
                    }, 401)
        except KeyError:
            raise AuthError({
                "code": "key_error",
                "description": "User is not logged in"
            }, 401)
        return func(*args, **kwargs)

    return decorated


def clear_user_session_keys():
    """
        Clear keys from the session that are relevent to the user.
        Used at logout
    """
    for key in KEYS_TO_CLEAR:
        session.pop(key)
