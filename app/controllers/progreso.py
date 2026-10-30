"""CU-06 Consultar historial de progreso (HU-06, RF-08)."""
from flask import Blueprint, render_template
from flask_login import current_user

from app.models import Rol
from app.services import MetricaService
from app.controllers.decoradores import rol_requerido

bp = Blueprint("progreso", __name__)


@bp.route("/mi-progreso")
@rol_requerido(Rol.SOCIO)
def mi_progreso():
    socio = current_user.persona
    historial = MetricaService.historial(socio.id_persona)
    membresia = socio.membresia_vigente()
    etiquetas = [m.fecha.strftime("%d/%m") for m in historial]
    return render_template("progreso/mi_progreso.html", socio=socio, historial=historial, membresia=membresia,
                           etiquetas=etiquetas)
