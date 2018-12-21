from app import db
from app.models import User


def create_tables():
    with db:
        db.create_tables([User])

if __name__ == "__main__":
    create_tables()
