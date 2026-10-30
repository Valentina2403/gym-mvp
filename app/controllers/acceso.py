"""AccesoController: CU-03 Validar acceso (HU-02)."""
from flask import Blueprint, render_template, request

from app.models import Rol
from app.repositories import RegistroAccesoRepository
from app.services import AccesoService
from app.controllers.decoradores import empleado_actual, rol_requerido

bp = Blueprint("acceso", __name__, url_prefix="/acceso")


@bp.route("/", methods=["GET", "POST"])
@rol_requerido(Rol.RECEPCIONISTA)
def validar():
    resultado = None
    if request.method == "POST":
        resultado = AccesoService.validar_acceso(request.form.get("documento", ""), empleado_actual())
    recientes = RegistroAccesoRepository.find_recientes(8)
    return render_template("acceso/validar.html", resultado=resultado, recientes=recientes)
