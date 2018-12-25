from datetime import datetime

from app.models import BaseModel
from playhouse.postgres_ext import (BooleanField, CharField, DateTimeField,
                                    JSONField, PrimaryKeyField)


class Chat(BaseModel):
    chat_id = PrimaryKeyField()
    chat_blob = JSONField(default={})
    name = CharField()
    created_date = DateTimeField(default=datetime.now)
