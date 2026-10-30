"""CU-01 Iniciar sesión (RF-06, RNF-03)."""
from app.models import Cuenta, Persona, Rol
from app.repositories import CuentaRepository
from app.services.errores import CorreoDuplicadoError, CredencialesInvalidasError


class AuthService:
    @staticmethod
    def autenticar(usuario: str, contrasena: str) -> Cuenta:
        cuenta = CuentaRepository.find_by_usuario(usuario or "")
        # Mismo mensaje en ambos casos: no se revela qué dato falló.
        if cuenta is None or not cuenta.autenticar(contrasena):
            raise CredencialesInvalidasError()
        return cuenta

    @staticmethod
    def crear_cuenta(persona: Persona, rol: Rol, contrasena: str) -> Cuenta:
        if CuentaRepository.find_by_usuario(persona.correo):
            raise CorreoDuplicadoError(persona.correo)
        cuenta = Cuenta(usuario=persona.correo, rol=rol, activa=True, persona=persona)
        cuenta.establecer_contrasena(contrasena)
        return cuenta
