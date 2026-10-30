"""SocioController: CU-02 Registrar socio y consulta de socios."""
from datetime import date

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from app.models import Rol
from app.repositories import SocioRepository
from app.services import SocioService
from app.services.errores import ErrorNegocio, ValidacionError
from app.controllers.decoradores import rol_requerido

bp = Blueprint("socios", __name__, url_prefix="/socios")


@bp.route("/")
@rol_requerido(Rol.RECEPCIONISTA, Rol.ENTRENADOR)
def listar():
    texto = request.args.get("q", "")
    return render_template("socios/listar.html", socios=SocioService.listar(texto), q=texto, hoy=date.today())


@bp.route("/nuevo", methods=["GET", "POST"])
@rol_requerido(Rol.RECEPCIONISTA)
def nuevo():
    datos, errores = {}, {}
    if request.method == "POST":
        datos = request.form.to_dict()
        try:
            socio = SocioService.registrar(datos)
        except ValidacionError as error:
            errores = error.campos
            flash(str(error), "danger")
        except ErrorNegocio as error:
            errores = {"documento": str(error)}
            flash(str(error), "danger")
        else:
            flash(f"Socio {socio.nombre_completo()} registrado con éxito. "
                  f"Usuario: {socio.correo} · contraseña temporal: su número de documento.", "success")
            return redirect(url_for("socios.listar"))
    return render_template("socios/nuevo.html", datos=datos, errores=errores), (422 if errores else 200)


@bp.route("/<int:id_socio>")
@rol_requerido(Rol.RECEPCIONISTA, Rol.ENTRENADOR)
def detalle(id_socio: int):
    socio = SocioRepository.find_by_id(id_socio) or abort(404)
    membresia = socio.membresia_vigente()
    if membresia:
        membresia.actualizar_estado()
    accesos = sorted(socio.registros_acceso, key=lambda r: r.fecha_hora, reverse=True)[:10]
    return render_template("socios/detalle.html", socio=socio, membresia=membresia, accesos=accesos,
                           hoy=date.today())

