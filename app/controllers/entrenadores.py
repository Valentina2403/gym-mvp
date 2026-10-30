"""EntrenadorController: CU-07 Registrar entrenador (HU-05)."""
from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.models import Rol
from app.repositories import EntrenadorRepository, EspecialidadRepository
from app.services import EntrenadorService
from app.services.errores import ErrorNegocio, ValidacionError
from app.controllers.decoradores import rol_requerido

bp = Blueprint("entrenadores", __name__, url_prefix="/entrenadores")


@bp.route("/")
@rol_requerido(Rol.ADMINISTRADOR)
def listar():
    return render_template("entrenadores/listar.html", entrenadores=EntrenadorRepository.find_all())


@bp.route("/nuevo", methods=["GET", "POST"])
@rol_requerido(Rol.ADMINISTRADOR)
def nuevo():
    datos, errores, seleccionadas = {}, {}, []
    if request.method == "POST":
        datos = request.form.to_dict()
        seleccionadas = [int(i) for i in request.form.getlist("especialidades") if i.isdigit()]
        try:
            entrenador = EntrenadorService.registrar(datos, seleccionadas)
        except ValidacionError as error:
            errores = error.campos
            flash(str(error), "danger")
        except ErrorNegocio as error:
            errores = {"documento": str(error)}
            flash(str(error), "danger")
        else:
            flash(f"Entrenador {entrenador.nombre_completo()} registrado y activo.", "success")
            return redirect(url_for("entrenadores.listar"))
    return render_template("entrenadores/nuevo.html", datos=datos, errores=errores, seleccionadas=seleccionadas,
                           especialidades=EspecialidadRepository.find_all()), (422 if errores else 200)
