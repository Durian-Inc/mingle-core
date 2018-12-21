# Import flask and template operators
from flask import Flask, render_template
# Import SQLAlchemy
from peewee import PostgresqlDatabase


# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object('config')

# Define the database object which is imported
# by modules and controllers
db = PostgresqlDatabase(
    'mingle', user='postgres', password='', host='127.0.0.1', port=5432)

from app.routes.controllers import routes

# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return error, 404


# Register blueprint(s)
app.register_blueprint(routes)
