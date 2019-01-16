"""Ties a third party auth id to a User in our database"""
from datetime import datetime

from app.models import BaseModel, User
from playhouse.postgres_ext import CharField, DateTimeField, ForeignKeyField


class AuthId(BaseModel):
    auth_id = CharField(unique=True, null=False)
    user = ForeignKeyField(User)
    date_created = DateTimeField(default=datetime.now)
