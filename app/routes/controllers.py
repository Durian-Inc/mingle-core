from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)

from app import db, CLIENT_ID, SECRET_KEY
from app.models import User
from app.routes.auth_utils import (auth0, requires_auth, urlencode, jsonify)

routes = Blueprint('routes', __name__, url_prefix='/')


@routes.route('/', methods=['GET'])
def home():
    stuff = [x.name for x in User.select()]
    return str(stuff)

@routes.route('/callback', methods=['GET'])
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
    return redirect('/user_info')

@routes.route('/login', methods=['GET'])
def login():
    return auth0.authorize_redirect(redirect_uri='http://localhost:8080/callback', audience='https://durian-inc.auth0.com/userinfo')

@routes.route('/logout')
def logout():
    # Clear session stored data
    session.clear()
    # Redirect user to logout endpoint
    params = {'returnTo': url_for('routes.home', _external=True), 'client_id': CLIENT_ID}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

@routes.route('/user_info', methods=['GET'])
@requires_auth
def user_info():
    return jsonify(session['jwt_payload'])

