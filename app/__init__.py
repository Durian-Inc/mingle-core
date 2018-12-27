from flask import Flask, render_template
from playhouse.postgres_ext import PostgresqlExtDatabase

app = Flask(__name__)

app.config.from_object('config')

db = PostgresqlExtDatabase(
    'mingle', user='postgres', password='', host='127.0.0.1', port=5432)

from app.serve import app
from app.users.controllers import users
from app.chats.controllers import chats
from app.auth_utils import auth


@app.errorhandler(404)
def not_found(error):
    print(error)
    return error, 404


app.register_blueprint(users)
app.register_blueprint(chats)
app.register_blueprint(auth)