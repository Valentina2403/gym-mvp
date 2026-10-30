"""Enumeraciones del dominio (ver diagrama de clases, Entregable 2)."""
import enum


class Rol(str, enum.Enum):
    ADMINISTRADOR = "ADMINISTRADOR"
    RECEPCIONISTA = "RECEPCIONISTA"
    ENTRENADOR = "ENTRENADOR"
    SOCIO = "SOCIO"


class EstadoMembresia(str, enum.Enum):
    ACTIVA = "ACTIVA"
    POR_VENCER = "POR_VENCER"
    VENCIDA = "VENCIDA"
    RENOVADA = "RENOVADA"
    CANCELADA = "CANCELADA"


class ResultadoAcceso(str, enum.Enum):
    PERMITIDO = "PERMITIDO"
    DENEGADO = "DENEGADO"


class MetodoPago(str, enum.Enum):
    EFECTIVO = "EFECTIVO"
    TRANSFERENCIA = "TRANSFERENCIA"
    DATAFONO = "DATAFONO"
