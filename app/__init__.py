import os

from dotenv import load_dotenv
from flask import Flask, render_template
from playhouse.postgres_ext import PostgresqlExtDatabase

from app.serve import app
from app.users.controllers import users
from app.chats.controllers import chats


@app.errorhandler(404)
def not_found(error):
    return error, 404


app.register_blueprint(users)
app.register_blueprint(chats)
