"""Fábrica de la aplicación Flask (arquitectura en capas MVC)."""
import os

import click
from flask import Flask, render_template

from app.config import CONFIGS
from app.extensions import csrf, db, login_manager


def create_app(config_name: str | None = None) -> Flask:
    config_name = config_name or os.environ.get("FLASK_ENV_NAME", "development")
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(CONFIGS[config_name])
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)


    from app.models import Cuenta, EstadoMembresia, Rol

    @login_manager.user_loader
    def cargar_cuenta(id_cuenta: str):
        return db.session.get(Cuenta, int(id_cuenta))

    @app.context_processor
    def variables_globales():
        return {"Rol": Rol, "EstadoMembresia": EstadoMembresia, "existe": lambda endpoint: endpoint in app.view_functions}

    @app.template_filter("fecha")
    def formato_fecha(valor):
        return valor.strftime("%d/%m/%Y") if valor else "—"

    @app.template_filter("dinero")
    def formato_dinero(valor):
        return f"$ {float(valor):,.0f}".replace(",", ".") if valor is not None else "—"

    @app.errorhandler(403)
    def prohibido(_error):
        return render_template("errores/403.html"), 403

    @app.errorhandler(404)
    def no_encontrado(_error):
        return render_template("errores/404.html"), 404

    registrar_comandos(app)
    return app


def registrar_comandos(app: Flask) -> None:
    @app.cli.command("init-db")
    def init_db():
        """Crea las tablas de la base de datos."""
        db.create_all()
        click.echo("Base de datos creada.")

    @app.cli.command("seed")
    @click.option("--reset", is_flag=True, help="Borra y vuelve a crear las tablas antes de cargar datos.")
    def seed(reset: bool):
        """Carga usuarios, planes y socios de demostración."""
        from app.seed import cargar_datos_demo
        if reset:
            db.drop_all()
        db.create_all()
        cargar_datos_demo()
        click.echo("Datos de demostración cargados.")

    @app.cli.command("actualizar-estados")
    def actualizar_estados():
        """Tarea diaria: recalcula el estado de las membresías."""
        from app.services import MembresiaService
        total = MembresiaService.actualizar_estados()
        click.echo(f"{total} membresías revisadas.")
