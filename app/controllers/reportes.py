"""ReporteController: CU-08 Generar reporte de morosos (HU-07, RF-05)."""
import csv
import io
from datetime import date

from flask import Blueprint, Response, render_template, request

from app.models import Rol
from app.services import ReporteService
from app.controllers.decoradores import rol_requerido

bp = Blueprint("reportes", __name__, url_prefix="/reportes")


@bp.route("/")
@rol_requerido(Rol.ADMINISTRADOR)
def generar():
    filtro = request.args.get("filtro", "morosos")
    generado = "generar" in request.args
    filas = []
    if generado:
        filas = ReporteService.activos() if filtro == "activos" else ReporteService.morosos()
    return render_template("reportes/generar.html", filtro=filtro, filas=filas, generado=generado,
                           hoy=date.today())


@bp.route("/exportar")
@rol_requerido(Rol.ADMINISTRADOR)
def exportar():
    filtro = request.args.get("filtro", "morosos")
    filas = ReporteService.activos() if filtro == "activos" else ReporteService.morosos()
    salida = io.StringIO()
    escritor = csv.writer(salida)
    escritor.writerow(["Nombre", "Documento", "Teléfono", "Fecha de vencimiento"])
    for fila in filas:
        escritor.writerow([fila["socio"].nombre_completo(), fila["socio"].documento, fila["telefono"],
                           fila["fecha_fin"].isoformat()])
    return Response(
        "﻿" + salida.getvalue(), mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=reporte_{filtro}_{date.today()}.csv"},
    )
