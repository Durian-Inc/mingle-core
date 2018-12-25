from app import app, CLIENT_ID, SECRET_KEY
from functools import wraps
import json
from werkzeug.exceptions import HTTPException

from flask import (Flask, jsonify, redirect, render_template, session, url_for)
from authlib.flask.client import OAuth
from six.moves.urllib.parse import urlencode

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

def requires_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    if 'profile' not in session:
      # Redirect to Login page here
      return redirect('/')
    return f(*args, **kwargs)

  return decorated