"""Validaciones de datos personales compartidas por socios y entrenadores."""
import re

from app.services.errores import ValidacionError

PATRON_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PATRON_DOCUMENTO = re.compile(r"^[0-9.]{5,15}$")
PATRON_TELEFONO = re.compile(r"^[0-9 +]{7,15}$")


def limpiar(datos: dict) -> dict:
    return {k: (v.strip() if isinstance(v, str) else v) for k, v in datos.items()}


def validar_datos_persona(datos: dict) -> dict:
    """Devuelve los datos limpios o lanza ValidacionError con los campos que fallan."""
    datos = limpiar(datos)
    errores: dict[str, str] = {}
    obligatorios = {
        "nombres": "Nombres", "apellidos": "Apellidos", "documento": "Documento",
        "correo": "Correo", "telefono": "Teléfono",
    }
    for campo, etiqueta in obligatorios.items():
        if not datos.get(campo):
            errores[campo] = f"{etiqueta} es obligatorio."
    if datos.get("documento") and not PATRON_DOCUMENTO.match(datos["documento"]):
        errores["documento"] = "Documento: solo números (5 a 15 caracteres)."
    if datos.get("correo") and not PATRON_CORREO.match(datos["correo"]):
        errores["correo"] = "Correo con formato inválido."
    if datos.get("telefono") and not PATRON_TELEFONO.match(datos["telefono"]):
        errores["telefono"] = "Teléfono: entre 7 y 15 dígitos."
    if errores:
        raise ValidacionError(errores)
    datos["correo"] = datos["correo"].lower()
    return datos
