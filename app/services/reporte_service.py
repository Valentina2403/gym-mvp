"""CU-08 Generar reporte de morosos (HU-07, RF-05)."""
from datetime import date

from app.extensions import db
from app.repositories import MembresiaRepository, RegistroAccesoRepository, SocioRepository


class ReporteService:
    @staticmethod
    def _membresias_actuales(hoy: date):
        membresias = MembresiaRepository.find_actuales()
        for membresia in membresias:
            membresia.actualizar_estado(hoy)
        db.session.commit()
        return membresias

    @staticmethod
    def morosos(hoy: date | None = None) -> list[dict]:
        hoy = hoy or date.today()
        filas = [
            {"socio": m.socio, "telefono": m.socio.telefono, "fecha_fin": m.fecha_fin,
             "dias_vencida": (hoy - m.fecha_fin).days}
            for m in ReporteService._membresias_actuales(hoy) if not m.esta_vigente(hoy)
        ]
        return sorted(filas, key=lambda f: f["fecha_fin"])

    @staticmethod
    def activos(hoy: date | None = None) -> list[dict]:
        hoy = hoy or date.today()
        filas = [
            {"socio": m.socio, "telefono": m.socio.telefono, "fecha_fin": m.fecha_fin,
             "plan": m.plan.nombre, "estado": m.estado}
            for m in ReporteService._membresias_actuales(hoy) if m.esta_vigente(hoy)
        ]
        return sorted(filas, key=lambda f: f["fecha_fin"])

    @staticmethod
    def resumen(hoy: date | None = None) -> dict:
        hoy = hoy or date.today()
        activos = ReporteService.activos(hoy)
        return {
            "socios": len(SocioRepository.find_all()),
            "activos": len(activos),
            "por_vencer": sum(1 for f in activos if f["estado"].value == "POR_VENCER"),
            "morosos": len(ReporteService.morosos(hoy)),
            "ingresos_hoy": RegistroAccesoRepository.contar_desde(hoy),
        }
