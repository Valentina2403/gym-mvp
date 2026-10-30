"""Modelo de dominio (M de MVC). Refleja el diagrama de clases del Entregable 2."""
from app.models.enums import EstadoMembresia, MetodoPago, ResultadoAcceso, Rol
from app.models.membresias import Membresia, Pago, Plan
from app.models.operacion import MedicionFisica, RegistroAcceso
from app.models.personas import Cuenta, Empleado, Entrenador, Especialidad, Persona, Socio

__all__ = [
    "Rol", "EstadoMembresia", "ResultadoAcceso", "MetodoPago",
    "Persona", "Socio", "Empleado", "Entrenador", "Especialidad", "Cuenta",
    "Plan", "Membresia", "Pago", "RegistroAcceso", "MedicionFisica",
]
