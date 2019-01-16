"""Stores info for a group chat"""
from datetime import datetime

from app.models import BaseModel, Theme
from playhouse.postgres_ext import (CharField, DateTimeField, ForeignKeyField,
                                    JSONField, PrimaryKeyField)


class Chat(BaseModel):
    id = PrimaryKeyField()
    events = JSONField(default=[])
    name = CharField()
    created = DateTimeField(default=datetime.now().isoformat())
    theme = ForeignKeyField(Theme)
