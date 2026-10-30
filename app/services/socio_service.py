"""CU-02 Registrar socio (HU-01, RF-01)."""
from app.extensions import db
from app.models import Rol, Socio
from app.repositories import PersonaRepository, SocioRepository
from app.services.auth_service import AuthService
from app.services.errores import DocumentoDuplicadoError
from app.services.validaciones import validar_datos_persona


class SocioService:
    @staticmethod
    def registrar(datos: dict) -> Socio:
        datos = validar_datos_persona(datos)
        # «include» Verificar documento único
        if PersonaRepository.find_by_documento(datos["documento"]):
            raise DocumentoDuplicadoError(datos["documento"])
        socio = Socio(
            nombres=datos["nombres"], apellidos=datos["apellidos"], documento=datos["documento"],
            correo=datos["correo"], telefono=datos["telefono"],
        )
        try:
            # Contraseña temporal: el número de documento (se cambia en "Mi cuenta").
            AuthService.crear_cuenta(socio, Rol.SOCIO, datos["documento"])
            SocioRepository.save(socio)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return socio

    @staticmethod
    def listar(texto: str | None = None) -> list[Socio]:
        return SocioRepository.find_all(texto)
