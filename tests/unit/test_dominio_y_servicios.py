"""Pruebas unitarias PU-01 a PU-14 (plan de pruebas, Entregable 2, sección 4.1)."""
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

import pytest

from app.models import (
    EstadoMembresia, MedicionFisica, Membresia, Plan, ResultadoAcceso, Rol, Socio,
)
from app.services import AccesoService, AuthService, EntrenadorService, MembresiaService, ReporteService, SocioService
from app.services.errores import DocumentoDuplicadoError, ValidacionError

pytestmark = pytest.mark.unit

FIN = date(2026, 11, 30)


def membresia(fin=FIN, dias_plan=30, estado=EstadoMembresia.ACTIVA):
    plan = Plan(nombre="Mensual", duracion_dias=dias_plan, precio=Decimal("90000"))
    return Membresia(plan=plan, fecha_inicio=fin - timedelta(days=dias_plan), fecha_fin=fin, estado=estado)


# ---------- Membresia.esta_vigente (HU-02) ----------

def test_PU01_membresia_vigente_antes_del_vencimiento():
    assert membresia().esta_vigente(FIN - timedelta(days=1)) is True


def test_PU02_membresia_vigente_el_dia_exacto_del_vencimiento():
    """Valor límite: el último día de la membresía todavía permite el ingreso."""
    assert membresia().esta_vigente(FIN) is True


def test_PU03_membresia_no_vigente_despues_del_vencimiento():
    assert membresia().esta_vigente(FIN + timedelta(days=1)) is False


def test_PU03b_membresia_renovada_o_cancelada_nunca_esta_vigente():
    assert membresia(estado=EstadoMembresia.RENOVADA).esta_vigente(FIN - timedelta(days=3)) is False
    assert membresia(estado=EstadoMembresia.CANCELADA).esta_vigente(FIN - timedelta(days=3)) is False


# ---------- Plan.calcular_fecha_fin (HU-04) ----------

def test_PU04_plan_mensual_suma_30_dias():
    plan = Plan(nombre="Mensual", duracion_dias=30, precio=Decimal("90000"))
    assert plan.calcular_fecha_fin(date(2026, 10, 29)) == date(2026, 11, 28)


# ---------- Membresia.actualizar_estado (diagrama de estados) ----------

@pytest.mark.parametrize("dias_restantes, esperado", [
    (8, EstadoMembresia.ACTIVA),
    (7, EstadoMembresia.POR_VENCER),
    (0, EstadoMembresia.POR_VENCER),
    (-1, EstadoMembresia.VENCIDA),
])
def test_PU05_transiciones_de_estado(app, dias_restantes, esperado):
    m = membresia()
    assert m.actualizar_estado(FIN - timedelta(days=dias_restantes)) == esperado


def test_PU05b_solo_se_cancela_una_membresia_activa():
    m = membresia(estado=EstadoMembresia.VENCIDA)
    with pytest.raises(ValueError):
        m.cancelar()
    activa = membresia()
    activa.cancelar()
    assert activa.estado == EstadoMembresia.CANCELADA


# ---------- MedicionFisica (HU-03, RF-04) ----------

def test_PU06_calculo_imc_ejemplo_de_la_historia():
    medicion = MedicionFisica(peso_kg=75, altura_m=1.75)
    assert medicion.calcular_imc() == 24.49


@pytest.mark.parametrize("peso, altura", [(75, 0), (-70, 1.70), (0, 1.70)])
def test_PU07_imc_rechaza_valores_invalidos(peso, altura):
    with pytest.raises(ValueError):
        MedicionFisica(peso_kg=peso, altura_m=altura).calcular_imc()


@pytest.mark.parametrize("imc, clasificacion", [
    (18.49, "Bajo peso"), (18.5, "Normal"), (24.99, "Normal"), (25.0, "Sobrepeso"), (29.99, "Sobrepeso"), (30, "Obesidad"),
])
def test_PU08_clasificacion_imc_en_valores_limite(imc, clasificacion):
    assert MedicionFisica(imc=imc).clasificacion_imc() == clasificacion


# ---------- SocioService / EntrenadorService (HU-01, HU-05) ----------

def test_PU09_registro_con_documento_duplicado_no_guarda(datos):
    with patch("app.services.socio_service.SocioRepository.save") as guardar:
        with pytest.raises(DocumentoDuplicadoError):
            SocioService.registrar({"nombres": "Otro", "apellidos": "Socio", "documento": "1000000001",
                                    "correo": "otro@test.com", "telefono": "3001234567"})
        guardar.assert_not_called()


def test_PU10_campos_obligatorios_vacios(datos):
    with pytest.raises(ValidacionError) as error:
        SocioService.registrar({"nombres": "Ana", "apellidos": "Ruiz", "documento": "", "correo": "",
                                "telefono": "3001234567"})
    assert set(error.value.campos) == {"documento", "correo"}

    with pytest.raises(ValidacionError) as error:
        EntrenadorService.registrar({"nombres": "Luis", "apellidos": "Mesa", "documento": "123456",
                                     "correo": "", "telefono": "3001234567"}, [])
    assert {"correo", "especialidades"} <= set(error.value.campos)


# ---------- AuthService (RNF-03) ----------

def test_PU11_contrasena_se_guarda_cifrada_con_bcrypt(datos):
    socio = Socio(nombres="Bea", apellidos="Toro", documento="555555", correo="bea@test.com", telefono="3000000000")
    cuenta = AuthService.crear_cuenta(socio, Rol.SOCIO, "Gym2026*")
    assert cuenta.hash_contrasena != "Gym2026*"
    assert cuenta.hash_contrasena.startswith("$2b$")  # identificador del algoritmo bcrypt
    assert cuenta.autenticar("Gym2026*") is True
    assert cuenta.autenticar("otra") is False


# ---------- AccesoService (HU-02) ----------

def test_PU12_acceso_denegado_con_membresia_vencida(datos):
    with patch("app.services.acceso_service.RegistroAccesoRepository.save") as guardar:
        resultado = AccesoService.validar_acceso("1000000003", datos["recepcion"])
    assert resultado.tipo == "DENEGADO"
    registro = guardar.call_args.args[0]
    assert registro.resultado == ResultadoAcceso.DENEGADO
    assert registro.motivo == "Membresía vencida"


# ---------- ReporteService (HU-07) ----------

def test_PU13_reporte_sin_morosos_devuelve_lista_vacia(datos):
    with patch("app.services.reporte_service.MembresiaRepository.find_actuales", return_value=[]):
        assert ReporteService.morosos() == []


# ---------- MembresiaService (HU-04) ----------

def test_PU14_renovar_marca_anterior_como_renovada(datos):
    socio = datos["activo"]
    anterior = socio.membresia_vigente()
    nueva = MembresiaService.renovar(socio.id_persona, datos["planes"]["mensual"].id_plan, "90000",
                                     "EFECTIVO", datos["admin"])
    assert anterior.estado == EstadoMembresia.RENOVADA
    assert nueva.estado in (EstadoMembresia.ACTIVA, EstadoMembresia.POR_VENCER)
    assert socio.membresia_vigente() is nueva
