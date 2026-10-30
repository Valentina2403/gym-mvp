"""Personas y acceso al sistema: Persona, Socio, Empleado, Entrenador, Especialidad, Cuenta."""
from datetime import date

import bcrypt
from flask import current_app
from flask_login import UserMixin

from app.extensions import db
from app.models.enums import EstadoMembresia, Rol

entrenador_especialidad = db.Table(
    "entrenador_especialidad",
    db.Column("id_entrenador", db.Integer, db.ForeignKey("persona.id_persona"), primary_key=True),
    db.Column("id_especialidad", db.Integer, db.ForeignKey("especialidad.id_especialidad"), primary_key=True),
)


class Persona(db.Model):
    """Clase abstracta del diagrama: se implementa con herencia de tabla única."""

    __tablename__ = "persona"
    id_persona = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), nullable=False)
    nombres = db.Column(db.String(80), nullable=False)
    apellidos = db.Column(db.String(80), nullable=False)
    documento = db.Column(db.String(20), nullable=False, unique=True, index=True)
    correo = db.Column(db.String(120), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)

    cuenta = db.relationship("Cuenta", back_populates="persona", uselist=False, cascade="all, delete-orphan")

    __mapper_args__ = {"polymorphic_on": tipo, "polymorphic_identity": "persona"}

    def nombre_completo(self) -> str:
        return f"{self.nombres} {self.apellidos}"


class Socio(Persona):
    fecha_registro = db.Column(db.Date, default=date.today)

    membresias = db.relationship(
        "Membresia", back_populates="socio", cascade="all, delete-orphan",
        order_by="Membresia.fecha_fin", foreign_keys="Membresia.id_socio"
    )
    mediciones = db.relationship(
        "MedicionFisica", back_populates="socio", cascade="all, delete-orphan",
        order_by="MedicionFisica.fecha", foreign_keys="MedicionFisica.id_socio"
    )
    registros_acceso = db.relationship(
        "RegistroAcceso", back_populates="socio", cascade="all, delete-orphan", foreign_keys="RegistroAcceso.id_socio"
    )

    __mapper_args__ = {"polymorphic_identity": "socio"}

    def membresia_vigente(self, fecha: date | None = None):
        """Última membresía que no fue renovada ni cancelada (puede estar vencida)."""
        candidatas = [
            m for m in self.membresias
            if m.estado not in (EstadoMembresia.RENOVADA, EstadoMembresia.CANCELADA)
        ]
        return max(candidatas, key=lambda m: m.fecha_fin, default=None)

    def esta_al_dia(self, fecha: date | None = None) -> bool:
        fecha = fecha or date.today()
        membresia = self.membresia_vigente(fecha)
        return membresia is not None and membresia.esta_vigente(fecha)


class Empleado(Persona):
    fecha_ingreso = db.Column(db.Date, default=date.today)
    __mapper_args__ = {"polymorphic_identity": "empleado"}


class Entrenador(Empleado):
    activo = db.Column(db.Boolean, default=True)
    especialidades = db.relationship("Especialidad", secondary=entrenador_especialidad, lazy="joined")
    __mapper_args__ = {"polymorphic_identity": "entrenador"}

    def asignar_especialidad(self, especialidad: "Especialidad") -> None:
        if especialidad not in self.especialidades:
            self.especialidades.append(especialidad)


class Especialidad(db.Model):
    __tablename__ = "especialidad"
    id_especialidad = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(60), nullable=False, unique=True)


class Cuenta(UserMixin, db.Model):
    __tablename__ = "cuenta"
    id_cuenta = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(120), nullable=False, unique=True, index=True)
    hash_contrasena = db.Column(db.String(128), nullable=False)
    rol = db.Column(db.Enum(Rol), nullable=False)
    activa = db.Column(db.Boolean, default=True, nullable=False)
    id_persona = db.Column(db.Integer, db.ForeignKey("persona.id_persona"), nullable=False, unique=True)

    persona = db.relationship("Persona", back_populates="cuenta")

    # Flask-Login
    def get_id(self) -> str:
        return str(self.id_cuenta)

    @property
    def is_active(self) -> bool:
        return bool(self.activa)

    def establecer_contrasena(self, contrasena: str) -> None:
        rondas = current_app.config.get("BCRYPT_ROUNDS", 12)
        self.hash_contrasena = bcrypt.hashpw(contrasena.encode(), bcrypt.gensalt(rondas)).decode()

    def autenticar(self, contrasena: str) -> bool:
        if not self.activa or not contrasena:
            return False
        return bcrypt.checkpw(contrasena.encode(), self.hash_contrasena.encode())

    def cambiar_contrasena(self, nueva: str) -> None:
        self.establecer_contrasena(nueva)

    def tiene_rol(self, *roles: Rol) -> bool:
        """El administrador hereda los permisos de Recepcionista y Entrenador (casos de uso)."""
        if self.rol == Rol.ADMINISTRADOR and Rol.SOCIO not in roles:
            return True
        return self.rol in roles
