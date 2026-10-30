"""Datos de demostración para la sustentación (comando: flask --app run seed --reset)."""
from datetime import date, datetime, timedelta
from decimal import Decimal

from app.extensions import db
from app.models import (
    Cuenta, Empleado, Entrenador, Especialidad, MedicionFisica, Membresia, MetodoPago, Pago, Plan,
    RegistroAcceso, ResultadoAcceso, Rol, Socio,
)

USUARIOS_DEMO = [
    # (nombres, apellidos, documento, correo, rol, contraseña)
    ("Laura", "Gómez", "1001001001", "admin@gimnasio.com", Rol.ADMINISTRADOR, "Admin2026*"),
    ("Camilo", "Restrepo", "1002002002", "recepcion@gimnasio.com", Rol.RECEPCIONISTA, "Recepcion2026*"),
]

SOCIOS_DEMO = [
    # (nombres, apellidos, documento, correo, teléfono, plan, días desde el inicio)
    ("Andrés", "Ramírez", "1037000111", "andres.ramirez@correo.com", "3001112233", "Mensual", 5),
    ("María", "López", "1037000222", "maria.lopez@correo.com", "3002223344", "Mensual", 25),
    ("Juliana", "Cardona", "1037000333", "juliana.cardona@correo.com", "3003334455", "Mensual", 40),
    ("Santiago", "Henao", "1037000444", "santiago.henao@correo.com", "3004445566", "Trimestral", 10),
    ("Valeria", "Ospina", "1037000555", "valeria.ospina@correo.com", "3005556677", "Mensual", 33),
    ("Daniel", "Zapata", "1037000666", "daniel.zapata@correo.com", "3006667788", "Anual", 100),
]


def _empleado(nombres, apellidos, documento, correo, rol, contrasena, clase=Empleado, **extra):
    persona = clase(nombres=nombres, apellidos=apellidos, documento=documento, correo=correo,
                    telefono="6044440000", **extra)
    cuenta = Cuenta(usuario=correo, rol=rol, persona=persona)
    cuenta.establecer_contrasena(contrasena)
    db.session.add(persona)
    return persona


def cargar_datos_demo(hoy: date | None = None) -> None:
    hoy = hoy or date.today()
    if Plan.query.first():
        return  # ya cargados

    planes = {
        "Mensual": Plan(nombre="Mensual", duracion_dias=30, precio=Decimal("90000")),
        "Trimestral": Plan(nombre="Trimestral", duracion_dias=90, precio=Decimal("240000")),
        "Anual": Plan(nombre="Anual", duracion_dias=365, precio=Decimal("850000")),
    }
    db.session.add_all(planes.values())
    especialidades = {n: Especialidad(nombre=n) for n in ("Musculación", "Crossfit", "Funcional", "Yoga", "Cardio")}
    db.session.add_all(especialidades.values())

    admin, recepcion = (_empleado(*u) for u in USUARIOS_DEMO)
    entrenador = _empleado("Felipe", "Arango", "1003003003", "entrenador@gimnasio.com", Rol.ENTRENADOR,
                           "Entrena2026*", clase=Entrenador, activo=True)
    entrenador.asignar_especialidad(especialidades["Musculación"])
    entrenador.asignar_especialidad(especialidades["Crossfit"])

    for nombres, apellidos, documento, correo, telefono, plan_nombre, dias in SOCIOS_DEMO:
        socio = Socio(nombres=nombres, apellidos=apellidos, documento=documento, correo=correo,
                      telefono=telefono, fecha_registro=hoy - timedelta(days=dias + 30))
        cuenta = Cuenta(usuario=correo, rol=Rol.SOCIO, persona=socio)
        cuenta.establecer_contrasena(documento)
        plan = planes[plan_nombre]
        inicio = hoy - timedelta(days=dias)
        membresia = Membresia(socio=socio, plan=plan, fecha_inicio=inicio, fecha_fin=plan.calcular_fecha_fin(inicio))
        membresia.asociar_pago(Pago(monto=plan.precio, metodo=MetodoPago.EFECTIVO, registrado_por=admin,
                                    fecha=datetime.combine(inicio, datetime.min.time()).replace(hour=9)))
        membresia.actualizar_estado(hoy)
        db.session.add(socio)

    # Historial físico del socio de demostración (Andrés Ramírez).
    andres = next(s for s in db.session.new if isinstance(s, Socio) and s.documento == "1037000111")
    for semanas, peso in ((16, 82.0), (12, 80.4), (8, 78.9), (4, 77.5)):
        medicion = MedicionFisica(socio=andres, registrada_por=entrenador, fecha=hoy - timedelta(weeks=semanas),
                                  peso_kg=peso, altura_m=1.78, porcentaje_grasa=round(22 - (16 - semanas) * 0.3, 1))
        medicion.calcular_imc()
        db.session.add(medicion)

    db.session.add(RegistroAcceso(socio=andres, validado_por=recepcion, resultado=ResultadoAcceso.PERMITIDO,
                                  fecha_hora=datetime.now() - timedelta(hours=2)))
    db.session.commit()
