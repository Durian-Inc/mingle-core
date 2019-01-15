"""Stores info for a theme"""
from app.models import BaseModel
from playhouse.postgres_ext import (CharField, PrimaryKeyField)


class Theme(BaseModel):
    id = PrimaryKeyField()
    name = CharField()
    bg_url = CharField()
    name_text_color = CharField(max_length=6)
    recieved_text_color = CharField(max_length=6)
    sent_text_color = CharField(max_length=6)
    snackbar_icon_color = CharField(max_length=6)
    recieved_bubble_bg = CharField(max_length=6)
    sent_bubble_bg = CharField(max_length=6)
    snackbar_bg = CharField(max_length=6)
