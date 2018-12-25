from playhouse.postgres_ext import Model

from app import db


class BaseModel(Model):
    class Meta:
        database = db
