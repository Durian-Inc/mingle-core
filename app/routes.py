from flask import Flask
from peewee import PostgresqlDatabase

# config - aside from our database, the rest is for use by Flask
DATABASE = 'tweepee.db'
DEBUG = True
SECRET_KEY = 'hin6bab8ge25*r=x&amp;+5$0kn=-#log$pt^#@vrqjld!^2ci@g*b'

app = Flask(__name__)

database = PostgresqlDatabase(
    'mingle', user='postgres', password='', host='127.0.0.1', port=5432)
