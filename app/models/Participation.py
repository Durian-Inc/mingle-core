"""The relationship between a User and a Chat"""
from app.models import BaseModel, User, Chat
from playhouse.postgres_ext import BooleanField, ForeignKeyField, IntegerField, Check


class Participation(BaseModel):
    chat = ForeignKeyField(Chat)
    user = ForeignKeyField(User)
    cursor = IntegerField(default=0)
    is_admin = BooleanField(default=0)

    class Meta:
        indexes = ((('chat', 'user'), True), )
