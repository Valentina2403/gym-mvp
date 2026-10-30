"""Fixtures compartidas: aplicación de pruebas con base de datos en memoria."""
from datetime import date, timedelta
from decimal import Decimal

import pytest

from app import create_app
from app.extensions import db as _db
from app.models import Cuenta, Empleado, Entrenador, Especialidad, Membresia, MetodoPago, Pago, Plan, Rol, Socio

HOY = date.today()  # las pruebas de integración usan la fecha real del servidor


@pytest.fixture()
def app():
    aplicacion = create_app("testing")
    with aplicacion.app_context():
        _db.create_all()
        yield aplicacion
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def db(app):
    return _db


@pytest.fixture()
def client(app):
    return app.test_client()


def _empleado(nombre, documento, correo, rol, contrasena, clase=Empleado, **extra):
    persona = clase(nombres=nombre, apellidos="Prueba", documento=documento, correo=correo,
                    telefono="6040000000", **extra)
    cuenta = Cuenta(usuario=correo, rol=rol, persona=persona)
    cuenta.establecer_contrasena(contrasena)
    _db.session.add(persona)
    return persona


@pytest.fixture()
def datos(db):
    """Escenario base: un usuario por rol, planes, especialidades y tres socios."""
    planes = {
        "mensual": Plan(nombre="Mensual", duracion_dias=30, precio=Decimal("90000")),
        "trimestral": Plan(nombre="Trimestral", duracion_dias=90, precio=Decimal("240000")),
    }
    db.session.add_all(planes.values())
    especialidades = [Especialidad(nombre="Musculación"), Especialidad(nombre="Crossfit")]
    db.session.add_all(especialidades)

    admin = _empleado("Admin", "900", "admin@test.com", Rol.ADMINISTRADOR, "Admin123*")
    recepcion = _empleado("Recepcion", "901", "recepcion@test.com", Rol.RECEPCIONISTA, "Recep123*")
    entrenador = _empleado("Entrenador", "902", "entrenador@test.com", Rol.ENTRENADOR, "Entrena123*",
                           clase=Entrenador, activo=True)

    def socio(nombre, documento, dias_desde_inicio=None, plan="mensual"):
        s = Socio(nombres=nombre, apellidos="Socio", documento=documento, correo=f"{nombre.lower()}@test.com",
                  telefono="3000000000")
        cuenta = Cuenta(usuario=s.correo, rol=Rol.SOCIO, persona=s)
        cuenta.establecer_contrasena(documento)
        if dias_desde_inicio is not None:
            inicio = HOY - timedelta(days=dias_desde_inicio)
            m = Membresia(socio=s, plan=planes[plan], fecha_inicio=inicio,
                          fecha_fin=planes[plan].calcular_fecha_fin(inicio))
            m.asociar_pago(Pago(monto=planes[plan].precio, metodo=MetodoPago.EFECTIVO, registrado_por=admin))
            m.actualizar_estado(HOY)
        db.session.add(s)
        return s

    activo = socio("Activo", "1000000001", dias_desde_inicio=5)        # vence en 25 días
    por_vencer = socio("Porvencer", "1000000002", dias_desde_inicio=25)  # vence en 5 días
    vencido = socio("Vencido", "1000000003", dias_desde_inicio=40)       # venció hace 10 días
    db.session.commit()
    return {
        "planes": planes, "especialidades": especialidades, "admin": admin, "recepcion": recepcion,
        "entrenador": entrenador, "activo": activo, "por_vencer": por_vencer, "vencido": vencido,
    }


def iniciar_sesion(client, usuario, contrasena):
    return client.post("/login", data={"usuario": usuario, "contrasena": contrasena})


@pytest.fixture()
def como(client, datos):
    """Inicia sesión con un rol: como('admin') / como('recepcion') / como('entrenador')."""
    credenciales = {
        "admin": ("admin@test.com", "Admin123*"),
        "recepcion": ("recepcion@test.com", "Recep123*"),
        "entrenador": ("entrenador@test.com", "Entrena123*"),
        "socio": ("activo@test.com", "1000000001"),
    }

    def _como(rol):
        client.get("/logout")
        iniciar_sesion(client, *credenciales[rol])
        return client

    return _como
