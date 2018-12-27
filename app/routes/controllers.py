from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)
from flask_cors import cross_origin

from app import db
from app.models import User
from app.routes.auth_utils import (requires_auth, jsonify, requires_scope)

routes = Blueprint('routes', __name__, url_prefix='/')


@routes.route('/', methods=['GET'])
def home():
    stuff = [x.name for x in User.select()]
    return str(stuff)

@routes.route("/api/public")
@cross_origin(headers=['Content-Type', 'Authorization'])
def public():
    """
        Route that requires no authentication.
    """
    response = "No login necessary"
    return jsonify(message=response)

@routes.route("/api/private")
@cross_origin(headers=['Content-Type', 'Authorization'])
@requires_auth
def private():
    """
        Route that requires authentication
    """
    response = "You are likely logged in so you good."
    return jsonify(message=response)
