from app.models import User, AuthId


def maybe_add_user(display_name, photo_url, auth_id):
    try:
        if not AuthId.get(AuthId.auth_id == auth_id):
            user = User.create(display_name=display_name, photo_url=photo_url)
            AuthId.create(user=user, auth_id=auth_id)
        return None
    except Exception as e:
        return e
