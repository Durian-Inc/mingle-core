"""Utility functions for using authentication"""
from functools import wraps

from flask import jsonify, session

from app.serve import CLIENT_ID, SECRET_KEY, app
from authlib.flask.client import OAuth

oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id=CLIENT_ID,
    client_secret=SECRET_KEY,
    api_base_url='https://durian-inc.auth0.com',
    access_token_url='https://durian-inc.auth0.com/oauth/token',
    authorize_url='https://durian-inc.auth0.com/authorize',
    client_kwargs={
        'scope': 'openid profile',
    },
)

# TODO: Make above urls environment variables


def requires_auth(func):
    """Decorator to specify that function needs to be authenticated"""

    @wraps(func)
    def decorated(*args, **kwargs):
        """Check authentication, or get failure"""
        if 'profile' not in session:
            # Redirect to Login page here
            return jsonify(success=False, error="Authentication failure")
        return func(*args, **kwargs)

    return decorated
