"""CU-05 Registrar métricas físicas (HU-03, RF-04) y CU-06 Consultar historial (HU-06, RF-08)."""
from datetime import date

from app.extensions import db
from app.models import Empleado, MedicionFisica
from app.repositories import MedicionRepository, SocioRepository
from app.services.errores import NoEncontradoError, ValidacionError


def _numero(valor, campo: str, errores: dict, obligatorio: bool = True):
    if valor in (None, ""):
        if obligatorio:
            errores[campo] = "Campo obligatorio."
        return None
    try:
        numero = float(str(valor).replace(",", "."))
    except ValueError:
        errores[campo] = "Debe ser un número."
        return None
    if numero <= 0:
        errores[campo] = "Debe ser mayor que cero."
        return None
    return numero


class MetricaService:
    @staticmethod
    def registrar_medicion(id_socio: int, peso, altura, grasa, empleado: Empleado,
                           hoy: date | None = None) -> MedicionFisica:
        errores: dict[str, str] = {}
        peso = _numero(peso, "peso", errores)
        altura = _numero(altura, "altura", errores)
        grasa = _numero(grasa, "grasa", errores, obligatorio=False)
        if altura is not None and altura > 3:
            errores["altura"] = "La altura va en metros (por ejemplo 1.75)."
        if grasa is not None and grasa >= 100:
            errores["grasa"] = "El porcentaje debe ser menor que 100."
        if errores:
            raise ValidacionError(errores)

        socio = SocioRepository.find_by_id(id_socio)
        if socio is None:
            raise NoEncontradoError("El socio no existe.")
        medicion = MedicionFisica(
            socio=socio, registrada_por=empleado, fecha=hoy or date.today(),
            peso_kg=peso, altura_m=altura, porcentaje_grasa=grasa,
        )
        medicion.calcular_imc()
        MedicionRepository.save(medicion)
        db.session.commit()
        return medicion

    @staticmethod
    def historial(id_socio: int) -> list[MedicionFisica]:
        return MedicionRepository.find_by_socio(id_socio)
