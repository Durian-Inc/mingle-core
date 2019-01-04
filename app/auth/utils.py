"""Utility functions for using authentication"""
from functools import wraps
import json

from flask import jsonify, session
from jose import jwt
from app.serve import CLIENT_ID, SECRET_KEY, app, AUTH0_DOMAIN, AUTHORIZE_URL, ACCESS_TOKEN_URL
from authlib.flask.client import OAuth
from six.moves.urllib.request import urlopen



ALGORITHMS = ["RS256"]

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