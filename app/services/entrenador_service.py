"""CU-07 Registrar entrenador (HU-05, RF-07)."""
from app.extensions import db
from app.models import Entrenador, Rol
from app.repositories import EspecialidadRepository, PersonaRepository
from app.services.auth_service import AuthService
from app.services.errores import DocumentoDuplicadoError, ValidacionError
from app.services.validaciones import validar_datos_persona


class EntrenadorService:
    @staticmethod
    def registrar(datos: dict, ids_especialidades: list[int]) -> Entrenador:
        errores = {}
        try:
            datos = validar_datos_persona(datos)
        except ValidacionError as error:
            errores.update(error.campos)
        especialidades = EspecialidadRepository.find_by_ids(ids_especialidades)
        if not especialidades:  # multiplicidad 1..* del diagrama de clases
            errores["especialidades"] = "Selecciona al menos una especialidad."
        if errores:
            raise ValidacionError(errores)
        if PersonaRepository.find_by_documento(datos["documento"]):
            raise DocumentoDuplicadoError(datos["documento"])

        entrenador = Entrenador(
            nombres=datos["nombres"], apellidos=datos["apellidos"], documento=datos["documento"],
            correo=datos["correo"], telefono=datos["telefono"], activo=True,
        )
        for especialidad in especialidades:
            entrenador.asignar_especialidad(especialidad)
        try:
            AuthService.crear_cuenta(entrenador, Rol.ENTRENADOR, datos["documento"])
            db.session.add(entrenador)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return entrenador
