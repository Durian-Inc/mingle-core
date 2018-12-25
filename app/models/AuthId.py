from app.models import BaseModel, User
from playhouse.postgres_ext import CharField, ForeignKeyField


class AuthId(BaseModel):
    auth_id = CharField()
    user = ForeignKeyField(User, backref='auth_id')
