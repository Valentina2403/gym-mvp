"""Operación diaria: RegistroAcceso y MedicionFisica."""
from datetime import date, datetime

from app.extensions import db
from app.models.enums import ResultadoAcceso


class RegistroAcceso(db.Model):
    __tablename__ = "registro_acceso"
    id_registro = db.Column(db.Integer, primary_key=True)
    id_socio = db.Column(db.Integer, db.ForeignKey("persona.id_persona"), nullable=False, index=True)
    id_empleado = db.Column(db.Integer, db.ForeignKey("persona.id_persona"), nullable=False)
    fecha_hora = db.Column(db.DateTime, nullable=False, default=datetime.now)
    resultado = db.Column(db.Enum(ResultadoAcceso), nullable=False)
    motivo = db.Column(db.String(120))

    socio = db.relationship("Socio", back_populates="registros_acceso", foreign_keys=[id_socio])
    validado_por = db.relationship("Empleado", foreign_keys=[id_empleado])


class MedicionFisica(db.Model):
    __tablename__ = "medicion_fisica"
    id_medicion = db.Column(db.Integer, primary_key=True)
    id_socio = db.Column(db.Integer, db.ForeignKey("persona.id_persona"), nullable=False, index=True)
    id_empleado = db.Column(db.Integer, db.ForeignKey("persona.id_persona"), nullable=False)
    fecha = db.Column(db.Date, nullable=False, default=date.today)
    peso_kg = db.Column(db.Float, nullable=False)
    altura_m = db.Column(db.Float, nullable=False)
    porcentaje_grasa = db.Column(db.Float, nullable=True)  # multiplicidad [0..1]
    imc = db.Column(db.Float, nullable=False)

    socio = db.relationship("Socio", back_populates="mediciones", foreign_keys=[id_socio])
    registrada_por = db.relationship("Empleado", foreign_keys=[id_empleado])

    def calcular_imc(self) -> float:
        """IMC = peso / altura², redondeado a 2 decimales (HU-03)."""
        if not self.peso_kg or not self.altura_m or self.peso_kg <= 0 or self.altura_m <= 0:
            raise ValueError("El peso y la altura deben ser mayores que cero.")
        self.imc = round(self.peso_kg / (self.altura_m ** 2), 2)
        return self.imc

    def clasificacion_imc(self) -> str:
        """Rangos de la Organización Mundial de la Salud."""
        imc = self.imc
        if imc < 18.5:
            return "Bajo peso"
        if imc < 25:
            return "Normal"
        if imc < 30:
            return "Sobrepeso"
        return "Obesidad"
