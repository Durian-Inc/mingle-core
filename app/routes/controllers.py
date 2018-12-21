# Import flask dependencies
from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)

# Import the database object from the main app module
from app import db
# Import module models (i.e. User)
from app.models import User

# Define the blueprint: 'auth', set its url prefix: app.url/auth
routes = Blueprint('routes', __name__, url_prefix='/')


# Set the route and accepted methods
@routes.route('/', methods=['GET'])
def home():
    stuff = [x.name for x in User.select()]
    return str(stuff)
