from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)

from app import db
from app.models import User

routes = Blueprint('routes', __name__, url_prefix='/')


@routes.route('/', methods=['GET'])
def home():
    stuff = [x.name for x in User.select()]
    return str(stuff)
