"""AuthController: CU-01 Iniciar sesión y cambio de contraseña."""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db
from app.services import AuthService
from app.services.errores import CredencialesInvalidasError

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.inicio"))
    if request.method == "POST":
        try:
            cuenta = AuthService.autenticar(request.form.get("usuario", ""), request.form.get("contrasena", ""))
        except CredencialesInvalidasError as error:
            flash(str(error), "danger")
            return render_template("auth/login.html", usuario=request.form.get("usuario", "")), 401
        login_user(cuenta)
        return redirect(url_for("main.inicio"))
    return render_template("auth/login.html")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("auth.login"))


@bp.route("/cuenta", methods=["GET", "POST"])
@login_required
def cuenta():
    if request.method == "POST":
        actual = request.form.get("actual", "")
        nueva = request.form.get("nueva", "")
        confirmacion = request.form.get("confirmacion", "")
        if not current_user.autenticar(actual):
            flash("La contraseña actual no es correcta.", "danger")
        elif len(nueva) < 8:
            flash("La nueva contraseña debe tener al menos 8 caracteres.", "danger")
        elif nueva != confirmacion:
            flash("La confirmación no coincide.", "danger")
        else:
            current_user.cambiar_contrasena(nueva)
            db.session.commit()
            flash("Contraseña actualizada.", "success")
            return redirect(url_for("main.inicio"))
    return render_template("auth/cuenta.html")
