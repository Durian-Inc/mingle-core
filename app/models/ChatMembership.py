from app.models import BaseModel, User, Chat
from playhouse.postgres_ext import CharField, ForeignKeyField, IntegerField


class ChatMembership(BaseModel):
    chat = ForeignKeyField(Chat, backref='membership')
    user = ForeignKeyField(User, backref='membership')
    cursor = IntegerField(default=0)
    rank = CharField(default="member")
