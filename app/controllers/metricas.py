"""MetricaController: CU-05 Registrar métricas físicas y calcular IMC (HU-03)."""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from app.models import Rol
from app.repositories import SocioRepository
from app.services import MetricaService
from app.services.errores import ErrorNegocio, ValidacionError
from app.controllers.decoradores import empleado_actual, rol_requerido

bp = Blueprint("metricas", __name__)


@bp.route("/socios/<int:id_socio>/metricas", methods=["GET", "POST"])
@rol_requerido(Rol.ENTRENADOR)
def registrar(id_socio: int):
    socio = SocioRepository.find_by_id(id_socio) or abort(404)
    datos, errores, medicion = {}, {}, None
    if request.method == "POST":
        datos = request.form.to_dict()
        try:
            medicion = MetricaService.registrar_medicion(
                socio.id_persona, datos.get("peso"), datos.get("altura"), datos.get("grasa"), empleado_actual()
            )
        except ValidacionError as error:
            errores = error.campos
            flash(str(error), "danger")
        except ErrorNegocio as error:
            flash(str(error), "danger")
        else:
            flash(f"Medición guardada. IMC {medicion.imc:.2f} ({medicion.clasificacion_imc()}).", "success")
            return redirect(url_for("metricas.registrar", id_socio=socio.id_persona))
    historial = MetricaService.historial(socio.id_persona)
    return render_template("metricas/registrar.html", socio=socio, datos=datos, errores=errores,
                           historial=historial), (422 if errores else 200)
