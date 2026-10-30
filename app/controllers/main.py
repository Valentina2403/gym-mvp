"""Panel de inicio según el rol."""
from flask import Blueprint, abort, current_app, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.models import Rol
from app.repositories import RegistroAccesoRepository
from app.services import ReporteService

bp = Blueprint("main", __name__)


@bp.route("/")
@login_required
def inicio():
    if current_user.rol == Rol.SOCIO:
        if "progreso.mi_progreso" not in current_app.view_functions:
            abort(403)
        return redirect(url_for("progreso.mi_progreso"))
    resumen = ReporteService.resumen()
    recientes = RegistroAccesoRepository.find_recientes(8)
    return render_template("main/inicio.html", resumen=resumen, recientes=recientes)
