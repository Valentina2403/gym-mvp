"""Pruebas de integración PI-01 a PI-10: controlador → servicio → repositorio → base de datos."""
import time
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

import pytest

from app.models import (
    Entrenador, EstadoMembresia, MedicionFisica, Membresia, Pago, Plan, RegistroAcceso, ResultadoAcceso, Rol, Socio,
)
from tests.conftest import iniciar_sesion

pytestmark = pytest.mark.integration


def texto(respuesta) -> str:
    return respuesta.get_data(as_text=True)


# PI-01 · RF-06: autenticación y autorización por rol
@pytest.mark.parametrize("usuario, contrasena, destino", [
    ("admin@test.com", "Admin123*", "/"),
    ("recepcion@test.com", "Recep123*", "/"),
    ("entrenador@test.com", "Entrena123*", "/"),
    ("activo@test.com", "1000000001", "/"),
])
def test_PI01_login_por_rol_redirige_al_panel(client, datos, usuario, contrasena, destino):
    respuesta = iniciar_sesion(client, usuario, contrasena)
    assert respuesta.status_code == 302 and respuesta.headers["Location"] == destino


def test_PI01b_credenciales_invalidas_no_revelan_el_dato(client, datos):
    for usuario, contrasena in [("admin@test.com", "mala"), ("noexiste@test.com", "Admin123*")]:
        respuesta = iniciar_sesion(client, usuario, contrasena)
        assert respuesta.status_code == 401
        assert "Usuario o contraseña incorrectos" in texto(respuesta)


def test_PI01c_rutas_no_permitidas_devuelven_403(como):
    assert como("recepcion").get("/reportes/").status_code == 403
    assert como("entrenador").get("/acceso/").status_code == 403
    assert como("socio").get("/socios/").status_code == 403
    assert como("admin").get("/acceso/").status_code == 200  # el administrador hereda permisos


# PI-02 · HU-01 escenarios 1 y 2
def test_PI02_registro_de_socio_y_documento_duplicado(como, db):
    cliente = como("recepcion")
    nuevo = {"nombres": "Sara", "apellidos": "Montoya", "documento": "1037000777",
             "correo": "sara@test.com", "telefono": "3017778899"}
    respuesta = cliente.post("/socios/nuevo", data=nuevo, follow_redirects=True)
    assert "registrado con éxito" in texto(respuesta)
    assert "Sara Montoya" in texto(cliente.get("/socios/"))
    assert Socio.query.filter_by(documento="1037000777").one().cuenta.rol == Rol.SOCIO

    duplicado = dict(nuevo, correo="otra@test.com", nombres="Otra")
    respuesta = cliente.post("/socios/nuevo", data=duplicado)
    assert respuesta.status_code == 422
    assert "ya se encuentra registrado" in texto(respuesta)
    assert Socio.query.filter_by(documento="1037000777").count() == 1


# PI-03 · HU-02 escenario 1
def test_PI03_acceso_permitido_con_membresia_vigente(como, datos):
    respuesta = como("recepcion").post("/acceso/", data={"documento": "1000000002"})  # vence en 5 días
    assert "Acceso permitido" in texto(respuesta)
    assert "Porvencer Socio" in texto(respuesta)
    registro = RegistroAcceso.query.order_by(RegistroAcceso.id_registro.desc()).first()
    assert registro.resultado == ResultadoAcceso.PERMITIDO


# PI-04 · HU-02 escenario 2
def test_PI04_acceso_denegado_con_membresia_vencida(como, datos):
    respuesta = como("recepcion").post("/acceso/", data={"documento": "1000000003"})
    assert "Acceso denegado" in texto(respuesta)
    assert "Membresía vencida" in texto(respuesta)
    registro = RegistroAcceso.query.order_by(RegistroAcceso.id_registro.desc()).first()
    assert registro.resultado == ResultadoAcceso.DENEGADO


def test_PI04b_documento_no_registrado(como, datos):
    respuesta = como("recepcion").post("/acceso/", data={"documento": "4444444"})
    assert "Socio no registrado" in texto(respuesta)


# PI-05 · HU-04: renovación y rollback
def test_PI05_renovacion_suma_30_dias_y_guarda_pago(como, datos):
    socio, plan = datos["vencido"], datos["planes"]["mensual"]
    respuesta = como("admin").post(f"/socios/{socio.id_persona}/renovar",
                                   data={"id_plan": plan.id_plan, "monto": "90000", "metodo": "EFECTIVO"},
                                   follow_redirects=True)
    nueva = socio.membresia_vigente()
    assert nueva.fecha_fin == date.today() + timedelta(days=30)
    assert nueva.pago.monto == Decimal("90000")
    assert f"Membresía vigente hasta {nueva.fecha_fin:%d/%m/%Y}" in texto(respuesta)


def test_PI05b_error_al_guardar_hace_rollback(como, datos, db):
    socio, plan = datos["vencido"], datos["planes"]["mensual"]
    membresias_antes, pagos_antes = Membresia.query.count(), Pago.query.count()
    cliente = como("admin")
    with patch("app.services.membresia_service.MembresiaRepository.save_all", side_effect=RuntimeError("falla BD")):
        with pytest.raises(RuntimeError):
            cliente.post(f"/socios/{socio.id_persona}/renovar",
                         data={"id_plan": plan.id_plan, "monto": "90000", "metodo": "EFECTIVO"})
    db.session.expire_all()
    assert Membresia.query.count() == membresias_antes
    assert Pago.query.count() == pagos_antes
    assert socio.membresia_vigente().estado != EstadoMembresia.RENOVADA


# PI-06 · HU-03 y HU-06 escenario 1
def test_PI06_medicion_calcula_imc_y_aparece_en_mi_progreso(como, datos):
    socio = datos["activo"]
    respuesta = como("entrenador").post(f"/socios/{socio.id_persona}/metricas",
                                        data={"peso": "75", "altura": "1.75", "grasa": ""}, follow_redirects=True)
    assert "IMC 24.49" in texto(respuesta)
    medicion = MedicionFisica.query.filter_by(id_socio=socio.id_persona).one()
    assert medicion.imc == 24.49 and medicion.fecha == date.today()
    assert "24.49" in texto(como("socio").get("/mi-progreso"))


def test_PI06b_medicion_con_datos_invalidos(como, datos):
    respuesta = como("entrenador").post(f"/socios/{datos['activo'].id_persona}/metricas",
                                        data={"peso": "abc", "altura": "0"})
    assert respuesta.status_code == 422
    assert MedicionFisica.query.count() == 0


# PI-07 · HU-07 escenario 1
def test_PI07_reporte_de_morosos_lista_solo_vencidos(como, datos):
    respuesta = como("admin").get("/reportes/?filtro=morosos&generar=1")
    html = texto(respuesta)
    assert "Vencido Socio" in html
    assert "Activo Socio" not in html and "Porvencer Socio" not in html
    assert "3000000000" in html  # teléfono
    csv = texto(como("admin").get("/reportes/exportar?filtro=morosos"))
    assert "1000000003" in csv and "1000000001" not in csv


# PI-08 · RNF-01: tiempo de respuesta de la validación de acceso
def test_PI08_validacion_de_acceso_menor_a_2_segundos(como, datos, db):
    plan = datos["planes"]["mensual"]
    hoy = date.today()
    for i in range(1000):
        socio = Socio(nombres=f"Carga{i}", apellidos="Prueba", documento=f"77{i:06d}",
                      correo=f"carga{i}@test.com", telefono="3000000000")
        socio.membresias.append(Membresia(plan=plan, fecha_inicio=hoy, fecha_fin=hoy + timedelta(days=30)))
        db.session.add(socio)
    db.session.commit()

    cliente = como("recepcion")
    tiempos = []
    for i in range(100):
        inicio = time.perf_counter()
        respuesta = cliente.post("/acceso/", data={"documento": f"77{i * 7:06d}"})
        tiempos.append(time.perf_counter() - inicio)
        assert respuesta.status_code == 200
    tiempos.sort()
    p95 = tiempos[94]
    print(f"\nRNF-01 · 100 validaciones con 1.003 socios: p95 = {p95 * 1000:.1f} ms, máx = {tiempos[-1] * 1000:.1f} ms")
    assert p95 < 2.0


# PI-09 · HU-06 escenario 2
def test_PI09_socio_sin_mediciones_ve_mensaje_amigable(como, datos):
    respuesta = como("socio").get("/mi-progreso")
    assert "Aún no tienes evaluaciones físicas registradas" in texto(respuesta)


# PI-10 · HU-05 escenario 1
def test_PI10_registro_de_entrenador_con_especialidades(como, datos):
    ids = [str(e.id_especialidad) for e in datos["especialidades"]]
    respuesta = como("admin").post("/entrenadores/nuevo", data={
        "nombres": "Natalia", "apellidos": "Vélez", "documento": "1003004004", "telefono": "3110001122",
        "correo": "natalia@test.com", "especialidades": ids,
    }, follow_redirects=True)
    assert "registrado y activo" in texto(respuesta)
    entrenador = Entrenador.query.filter_by(documento="1003004004").one()
    assert entrenador.activo and len(entrenador.especialidades) == 2
    assert entrenador.cuenta.rol == Rol.ENTRENADOR

