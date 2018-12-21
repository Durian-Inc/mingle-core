from peewee import CharField, DateTimeField

from app.models import BaseModel


class User(BaseModel):
    phone_number = CharField(unique=True)
    password = CharField()
    name = CharField()
