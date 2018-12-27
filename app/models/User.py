from datetime import datetime

from app.models import BaseModel
from playhouse.postgres_ext import BooleanField, CharField, DateTimeField, PrimaryKeyField


class User(BaseModel):
    user_id = PrimaryKeyField()
    phone_number = CharField(null=True)
    display_name = CharField()
    photo_url = CharField()
    created_date = DateTimeField(default=datetime.now)
