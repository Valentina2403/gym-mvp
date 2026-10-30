"""Membresías y pagos: Plan, Membresia, Pago."""
from datetime import date, datetime, timedelta
from decimal import Decimal

from flask import current_app, has_app_context

from app.extensions import db
from app.models.enums import EstadoMembresia, MetodoPago


def _dias_aviso() -> int:
    if has_app_context():
        return current_app.config.get("DIAS_AVISO_VENCIMIENTO", 7)
    return 7


class Plan(db.Model):
    __tablename__ = "plan"
    id_plan = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(60), nullable=False, unique=True)
    duracion_dias = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)

    def calcular_fecha_fin(self, inicio: date) -> date:
        return inicio + timedelta(days=self.duracion_dias)


class Membresia(db.Model):
    __tablename__ = "membresia"
    id_membresia = db.Column(db.Integer, primary_key=True)
    id_socio = db.Column(db.Integer, db.ForeignKey("persona.id_persona"), nullable=False, index=True)
    id_plan = db.Column(db.Integer, db.ForeignKey("plan.id_plan"), nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    estado = db.Column(db.Enum(EstadoMembresia), nullable=False, default=EstadoMembresia.ACTIVA)

    socio = db.relationship("Socio", back_populates="membresias")
    plan = db.relationship("Plan")
    pago = db.relationship("Pago", back_populates="membresia", uselist=False, cascade="all, delete-orphan")

    def esta_vigente(self, fecha: date | None = None) -> bool:
        fecha = fecha or date.today()
        if self.estado in (EstadoMembresia.CANCELADA, EstadoMembresia.RENOVADA):
            return False
        return self.fecha_inicio <= fecha <= self.fecha_fin

    def dias_restantes(self, fecha: date | None = None) -> int:
        fecha = fecha or date.today()
        return (self.fecha_fin - fecha).days

    def actualizar_estado(self, fecha: date | None = None) -> EstadoMembresia:
        """Aplica las transiciones con guarda del diagrama de estados."""
        fecha = fecha or date.today()
        if self.estado in (EstadoMembresia.CANCELADA, EstadoMembresia.RENOVADA):
            return self.estado
        if fecha > self.fecha_fin:
            self.estado = EstadoMembresia.VENCIDA
        elif self.dias_restantes(fecha) <= _dias_aviso():
            self.estado = EstadoMembresia.POR_VENCER
        else:
            self.estado = EstadoMembresia.ACTIVA
        return self.estado

    def asociar_pago(self, pago: "Pago") -> None:
        self.pago = pago

    def marcar_renovada(self) -> None:
        self.estado = EstadoMembresia.RENOVADA

    def cancelar(self) -> None:
        if self.estado != EstadoMembresia.ACTIVA:
            raise ValueError("Solo se puede cancelar una membresía en estado Activa.")
        self.estado = EstadoMembresia.CANCELADA


class Pago(db.Model):
    __tablename__ = "pago"
    id_pago = db.Column(db.Integer, primary_key=True)
    id_membresia = db.Column(db.Integer, db.ForeignKey("membresia.id_membresia"), nullable=False, unique=True)
    id_empleado = db.Column(db.Integer, db.ForeignKey("persona.id_persona"), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.now)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    metodo = db.Column(db.Enum(MetodoPago), nullable=False)

    membresia = db.relationship("Membresia", back_populates="pago")
    registrado_por = db.relationship("Empleado", foreign_keys=[id_empleado])

    @staticmethod
    def validar_monto(monto) -> Decimal:
        valor = Decimal(str(monto))
        if valor <= 0:
            raise ValueError("El monto del pago debe ser mayor que cero.")
        return valor
