from app import app
from functools import wraps
import json
from os import environ as env
from werkzeug.exceptions import HTTPException

from dotenv import (load_dotenv, find_dotenv)
from flask import (Flask, jsonify, redirect, render_template, session, url_for)
from authlib.flask.client import OAuth
from six.moves.urllib.parse import urlencode

oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id='CLIENT-ID',
    client_secret='SECRET-KEY',
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