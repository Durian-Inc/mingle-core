"""Stores info for a group chat"""
from datetime import datetime

from app.models import BaseModel
from playhouse.postgres_ext import (BooleanField, CharField, DateTimeField,
                                    JSONField, PrimaryKeyField)


class Chat(BaseModel):
    id = PrimaryKeyField()
    events = JSONField(default=[])
    name = CharField()
    date_created = DateTimeField(default=datetime.now)
    background = CharField(default="default")
