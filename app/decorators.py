from app.models import Permission
from flask.ext.login import current_user
from functools import wraps
from flask import abort
__author__ = 'py'


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_funcion(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_funcion
    return decorator


def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)


def user_required(f):
    return permission_required(Permission.MAKE_OPERATION)(f)

