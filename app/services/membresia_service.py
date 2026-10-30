"""CU-04 Asignar / renovar membresía (HU-04, RF-02). Sigue el diagrama de secuencia 3.1 c."""
from datetime import date

from app.extensions import db
from app.models import Empleado, Membresia, MetodoPago, Pago
from app.repositories import MembresiaRepository, PlanRepository, SocioRepository
from app.services.errores import NoEncontradoError, ValidacionError


class MembresiaService:
    @staticmethod
    def renovar(id_socio: int, id_plan: int, monto, metodo: str, admin: Empleado,
                hoy: date | None = None) -> Membresia:
        hoy = hoy or date.today()
        errores = {}
        try:
            monto = Pago.validar_monto(monto)
        except (ValueError, ArithmeticError):
            errores["monto"] = "Ingresa un monto mayor que cero."
        try:
            metodo = MetodoPago(metodo)
        except ValueError:
            errores["metodo"] = "Selecciona un método de pago."
        socio = SocioRepository.find_by_id(id_socio)
        plan = PlanRepository.find_by_id(id_plan) if id_plan else None
        if plan is None:
            errores["plan"] = "Selecciona un plan."
        if socio is None:
            raise NoEncontradoError("El socio no existe.")
        if errores:
            raise ValidacionError(errores)

        # Toda la operación es una sola transacción (@Transactional en el diseño).
        try:
            anterior = MembresiaRepository.find_vigente_by_socio(socio.id_persona)
            if anterior is not None:
                anterior.marcar_renovada()
            nueva = Membresia(socio=socio, plan=plan, fecha_inicio=hoy, fecha_fin=plan.calcular_fecha_fin(hoy))
            nueva.actualizar_estado(hoy)
            pago = Pago(monto=monto, metodo=metodo, registrado_por=admin)
            nueva.asociar_pago(pago)
            MembresiaRepository.save_all(anterior, nueva)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return nueva

    @staticmethod
    def cancelar(id_membresia: int) -> Membresia:
        membresia = db.session.get(Membresia, id_membresia)
        if membresia is None:
            raise NoEncontradoError("La membresía no existe.")
        membresia.cancelar()
        db.session.commit()
        return membresia

    @staticmethod
    def actualizar_estados(hoy: date | None = None) -> int:
        """Tarea diaria: aplica las transiciones de estado a todas las membresías actuales."""
        membresias = MembresiaRepository.find_actuales()
        for membresia in membresias:
            membresia.actualizar_estado(hoy)
        db.session.commit()
        return len(membresias)
