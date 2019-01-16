"""
Serves as the base for each model in the app, ties the database to the model
"""
from app.serve import db
from playhouse.postgres_ext import Model


class BaseModel(Model):
    class Meta:
        database = db
