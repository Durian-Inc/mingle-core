from app import db
from app.models import AuthId, User, Chat, ChatMembership


def create_tables():
    with db:
        db.create_tables([AuthId, User, Chat, ChatMembership])


if __name__ == "__main__":
    create_tables()
