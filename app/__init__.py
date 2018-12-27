from app.serve import app
from app.users.controllers import users
from app.chats.controllers import chats


@app.errorhandler(404)
def not_found(error):
    return error, 404


app.register_blueprint(users)
app.register_blueprint(chats)
