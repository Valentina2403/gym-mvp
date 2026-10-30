"""Configuración por entorno de la aplicación."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "cambie-esta-clave-en-produccion")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'instance' / 'gimnasio.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    # Días antes del vencimiento en que una membresía pasa a "Por vencer".
    DIAS_AVISO_VENCIMIENTO = int(os.environ.get("DIAS_AVISO_VENCIMIENTO", 7))
    BCRYPT_ROUNDS = int(os.environ.get("BCRYPT_ROUNDS", 12))


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    BCRYPT_ROUNDS = 4  # acelera las pruebas sin cambiar el algoritmo


class ProductionConfig(Config):
    DEBUG = False


CONFIGS = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
