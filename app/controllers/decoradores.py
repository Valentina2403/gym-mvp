"""Autorización por rol (RF-06). El administrador hereda permisos de recepción y entrenamiento."""
from functools import wraps

from flask import abort
from flask_login import current_user, login_required

from app.models import Rol


def rol_requerido(*roles: Rol):
    def decorador(vista):
        @wraps(vista)
        @login_required
        def envoltura(*args, **kwargs):
            if not current_user.tiene_rol(*roles):
                abort(403)
            return vista(*args, **kwargs)
        return envoltura
    return decorador


def empleado_actual():
    return current_user.persona
