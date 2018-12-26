from app.models import BaseModel, User, Chat
from playhouse.postgres_ext import CharField, ForeignKeyField, IntegerField


class ChatMembership(BaseModel):
    chat = ForeignKeyField(Chat)
    user = ForeignKeyField(User)
    cursor = IntegerField(default=0)
    rank = CharField(default="member")
