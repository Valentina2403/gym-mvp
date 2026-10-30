"""Servicios de negocio (M de MVC): reglas de los casos de uso CU-01 a CU-08."""
from app.services.auth_service import AuthService
from app.services.entrenador_service import EntrenadorService
from app.services.reporte_service import ReporteService
from app.services.socio_service import SocioService

__all__ = ["AuthService", "EntrenadorService", "ReporteService", "SocioService"]
