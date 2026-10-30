"""Capa de persistencia: repositorios (equivalentes a los *Repository del diagrama de secuencia)."""
from datetime import date

from sqlalchemy import func

from app.extensions import db
from app.models import (
    Cuenta, EstadoMembresia, Especialidad, MedicionFisica, Membresia, Persona, Plan, RegistroAcceso, Socio,
    Entrenador,
)


class CuentaRepository:
    @staticmethod
    def find_by_usuario(usuario: str) -> Cuenta | None:
        return Cuenta.query.filter(func.lower(Cuenta.usuario) == usuario.strip().lower()).first()

    @staticmethod
    def find_by_id(id_cuenta: int) -> Cuenta | None:
        return db.session.get(Cuenta, id_cuenta)


class PersonaRepository:
    @staticmethod
    def find_by_documento(documento: str) -> Persona | None:
        return Persona.query.filter_by(documento=documento.strip()).first()


class SocioRepository:
    @staticmethod
    def find_by_documento(documento: str) -> Socio | None:
        return Socio.query.filter_by(documento=documento.strip()).first()

    @staticmethod
    def find_by_id(id_socio: int) -> Socio | None:
        return db.session.get(Socio, id_socio)

    @staticmethod
    def find_all(texto: str | None = None) -> list[Socio]:
        consulta = Socio.query
        if texto:
            patron = f"%{texto.strip()}%"
            consulta = consulta.filter(
                db.or_(Socio.nombres.ilike(patron), Socio.apellidos.ilike(patron), Socio.documento.ilike(patron))
            )
        return consulta.order_by(Socio.apellidos, Socio.nombres).all()

    @staticmethod
    def save(socio: Socio) -> Socio:
        db.session.add(socio)
        return socio


class MembresiaRepository:
    @staticmethod
    def find_vigente_by_socio(id_socio: int) -> Membresia | None:
        """Membresía más reciente que no fue renovada ni cancelada."""
        return (
            Membresia.query.filter(
                Membresia.id_socio == id_socio,
                Membresia.estado.notin_([EstadoMembresia.RENOVADA, EstadoMembresia.CANCELADA]),
            )
            .order_by(Membresia.fecha_fin.desc())
            .first()
        )

    @staticmethod
    def find_actuales() -> list[Membresia]:
        return Membresia.query.filter(
            Membresia.estado.notin_([EstadoMembresia.RENOVADA, EstadoMembresia.CANCELADA])
        ).all()

    @staticmethod
    def save_all(*membresias: Membresia) -> None:
        for membresia in membresias:
            if membresia is not None:
                db.session.add(membresia)


class PlanRepository:
    @staticmethod
    def find_all() -> list[Plan]:
        return Plan.query.order_by(Plan.duracion_dias).all()

    @staticmethod
    def find_by_id(id_plan: int) -> Plan | None:
        return db.session.get(Plan, id_plan)


class RegistroAccesoRepository:
    @staticmethod
    def save(registro: RegistroAcceso) -> RegistroAcceso:
        db.session.add(registro)
        return registro

    @staticmethod
    def find_recientes(limite: int = 10) -> list[RegistroAcceso]:
        return RegistroAcceso.query.order_by(RegistroAcceso.fecha_hora.desc()).limit(limite).all()

    @staticmethod
    def contar_desde(fecha: date) -> int:
        return RegistroAcceso.query.filter(func.date(RegistroAcceso.fecha_hora) >= fecha).count()


class MedicionRepository:
    @staticmethod
    def save(medicion: MedicionFisica) -> MedicionFisica:
        db.session.add(medicion)
        return medicion

    @staticmethod
    def find_by_socio(id_socio: int) -> list[MedicionFisica]:
        return (
            MedicionFisica.query.filter_by(id_socio=id_socio)
            .order_by(MedicionFisica.fecha, MedicionFisica.id_medicion)
            .all()
        )


class EntrenadorRepository:
    @staticmethod
    def find_all() -> list[Entrenador]:
        return Entrenador.query.order_by(Entrenador.apellidos).all()


class EspecialidadRepository:
    @staticmethod
    def find_all() -> list[Especialidad]:
        return Especialidad.query.order_by(Especialidad.nombre).all()

    @staticmethod
    def find_by_ids(ids: list[int]) -> list[Especialidad]:
        if not ids:
            return []
        return Especialidad.query.filter(Especialidad.id_especialidad.in_(ids)).all()
