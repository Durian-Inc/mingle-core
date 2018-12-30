"""The relationship between a User and a Chat"""
from app.models import BaseModel, User, Chat
from playhouse.postgres_ext import CharField, ForeignKeyField, IntegerField


class Participation(BaseModel):
    chat = ForeignKeyField(Chat)
    user = ForeignKeyField(User)
    cursor = IntegerField(default=0)
    rank = CharField(default="member")
