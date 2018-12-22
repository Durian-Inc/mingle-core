from flask import Flask, render_template
from peewee import PostgresqlDatabase


app = Flask(__name__)

app.config.from_object('config')

db = PostgresqlDatabase(
    'mingle', user='postgres', password='', host='127.0.0.1', port=5432)

from app.routes.controllers import routes

@app.errorhandler(404)
def not_found(error):
    return error, 404


app.register_blueprint(routes)
