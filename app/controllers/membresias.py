"""MembresiaController: CU-04 Asignar / renovar membresía (HU-04)."""
from datetime import date

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from app.models import MetodoPago, Rol
from app.repositories import PlanRepository, SocioRepository
from app.services import MembresiaService
from app.services.errores import ErrorNegocio, ValidacionError
from app.controllers.decoradores import empleado_actual, rol_requerido

bp = Blueprint("membresias", __name__)


@bp.route("/socios/<int:id_socio>/renovar", methods=["GET", "POST"])
@rol_requerido(Rol.ADMINISTRADOR)
def renovar(id_socio: int):
    socio = SocioRepository.find_by_id(id_socio) or abort(404)
    planes = PlanRepository.find_all()
    datos, errores = {}, {}
    if request.method == "POST":
        datos = request.form.to_dict()
        try:
            nueva = MembresiaService.renovar(
                socio.id_persona, int(datos.get("id_plan") or 0), datos.get("monto"),
                datos.get("metodo", ""), empleado_actual(),
            )
        except ValidacionError as error:
            errores = error.campos
            flash(str(error), "danger")
        except ErrorNegocio as error:
            flash(str(error), "danger")
        else:
            flash(f"Membresía vigente hasta {nueva.fecha_fin:%d/%m/%Y}.", "success")
            return redirect(url_for("socios.detalle", id_socio=socio.id_persona))
    return render_template("membresias/renovar.html", socio=socio, planes=planes, metodos=list(MetodoPago),
                           datos=datos, errores=errores, hoy=date.today(),
                           actual=socio.membresia_vigente()), (422 if errores else 200)


@bp.route("/membresias/<int:id_membresia>/cancelar", methods=["POST"])
@rol_requerido(Rol.ADMINISTRADOR)
def cancelar(id_membresia: int):
    try:
        membresia = MembresiaService.cancelar(id_membresia)
    except (ErrorNegocio, ValueError) as error:
        flash(str(error), "danger")
        return redirect(request.referrer or url_for("socios.listar"))
    flash("Membresía cancelada.", "info")
    return redirect(url_for("socios.detalle", id_socio=membresia.id_socio))
