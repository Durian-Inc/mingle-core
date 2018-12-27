from flask import Flask, render_template
from playhouse.postgres_ext import PostgresqlExtDatabase

app = Flask(__name__)

app.config.from_object('config')

db = PostgresqlExtDatabase(
    'mingle', user='postgres', password='', host='127.0.0.1', port=5432)

from dotenv import load_dotenv
load_dotenv(dotenv_path='./.env')
import os
CLIENT_ID = os.getenv("CLIENT-ID")
SECRET_KEY = os.getenv("SECRET-KEY")
AUTH0_DOMAIN = os.getenv("AUTH0-DOMAIN")
API_AUDIENCE = os.getenv("API-AUDIENCE")

from app.users.controllers import users
from app.chats.controllers import chats


@app.errorhandler(404)
def not_found(error):
    return error, 404


app.register_blueprint(users)
app.register_blueprint(chats)
