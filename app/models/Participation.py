"""The relationship between a User and a Chat"""
from datetime import datetime
from app.models import BaseModel, User, Chat
from playhouse.postgres_ext import BooleanField, ForeignKeyField, IntegerField, Check, DateTimeField


class Participation(BaseModel):
    chat = ForeignKeyField(Chat)
    user = ForeignKeyField(User)
    cursor = IntegerField(default=0)
    is_admin = BooleanField(default=0)
    created = DateTimeField(default=datetime.now().isoformat())

    class Meta:
        indexes = ((('chat', 'user'), True), )
