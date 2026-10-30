"""CU-03 Validar acceso (HU-02, RF-03, RNF-01). Sigue el diagrama de secuencia 3.1 b."""
from dataclasses import dataclass
from datetime import date

from app.extensions import db
from app.models import Empleado, EstadoMembresia, Membresia, RegistroAcceso, ResultadoAcceso, Socio
from app.repositories import MembresiaRepository, RegistroAccesoRepository, SocioRepository


@dataclass
class ResultadoValidacion:
    tipo: str  # NO_REGISTRADO | PERMITIDO | DENEGADO
    mensaje: str
    socio: Socio | None = None
    membresia: Membresia | None = None
    dias_restantes: int | None = None

    @property
    def color(self) -> str:
        if self.tipo != "PERMITIDO":
            return "danger"
        return "warning" if self.por_vencer else "success"

    @property
    def por_vencer(self) -> bool:
        return self.membresia is not None and self.membresia.estado == EstadoMembresia.POR_VENCER


class AccesoService:
    @staticmethod
    def validar_acceso(documento: str, empleado: Empleado, hoy: date | None = None) -> ResultadoValidacion:
        hoy = hoy or date.today()
        socio = SocioRepository.find_by_documento(documento or "")
        if socio is None:
            return ResultadoValidacion("NO_REGISTRADO", "Socio no registrado")

        membresia = MembresiaRepository.find_vigente_by_socio(socio.id_persona)
        vigente = membresia is not None and membresia.esta_vigente(hoy)
        if membresia is not None:
            membresia.actualizar_estado(hoy)

        if vigente:
            registro = RegistroAcceso(socio=socio, validado_por=empleado, resultado=ResultadoAcceso.PERMITIDO)
            mensaje = f"Acceso permitido: {socio.nombre_completo()}"
            tipo = "PERMITIDO"
        else:
            motivo = "Membresía vencida" if membresia else "Sin membresía"
            registro = RegistroAcceso(
                socio=socio, validado_por=empleado, resultado=ResultadoAcceso.DENEGADO, motivo=motivo
            )
            mensaje = f"Acceso denegado: {motivo.lower()}"
            tipo = "DENEGADO"
        RegistroAccesoRepository.save(registro)
        db.session.commit()
        return ResultadoValidacion(
            tipo, mensaje, socio, membresia, membresia.dias_restantes(hoy) if membresia else None
        )
