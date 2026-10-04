"""
Implementación mock del repositorio de mantenciones.
"""
from copy import deepcopy
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from app.domain.models import Mantenimiento
from app.repositories.mantenimientos_repository import MantenimientosRepository


def _ahora_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hace_dias(dias: int) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=dias)
    return dt.isoformat()


_MANTENIMIENTOS_MOCK: List[Mantenimiento] = [
    Mantenimiento(
        id="mant-001",
        maquina_id="mq-004",
        maquina_nombre="Jalón al pecho en polea",
        fecha=_hace_dias(4),
        tipo="correctivo",
        gimnasio_id="mock-gym",
        notas="Se reemplazó el cable de acero y se lubricó la polea superior.",
        realizado_por_id="u-gim-001",
        realizado_por_nombre="Admin Gimnasio",
        origen="auto",
        reporte_id="rep-0001",
    ),
    Mantenimiento(
        id="mant-002",
        maquina_id="mq-009",
        maquina_nombre="Curl de bíceps con mancuernas",
        fecha=_hace_dias(4),
        tipo="revision",
        gimnasio_id="mock-gym",
        notas="Se repuso el agarre faltante de la mancuerna izquierda.",
        realizado_por_id="u-gim-001",
        realizado_por_nombre="Admin Gimnasio",
        origen="auto",
        reporte_id="rep-0002",
    ),
    Mantenimiento(
        id="mant-003",
        maquina_id="mq-005",
        maquina_nombre="Sentadilla con barra",
        fecha=_hace_dias(15),
        tipo="preventivo",
        gimnasio_id="mock-gym",
        notas="Ajuste general de tornillería y engrase de guías.",
        realizado_por_id="u-gim-001",
        realizado_por_nombre="Admin Gimnasio",
        origen="manual",
    ),
    Mantenimiento(
        id="mant-004",
        maquina_id="mq-006",
        maquina_nombre="Prensa de piernas 45°",
        fecha=_hace_dias(30),
        tipo="limpieza",
        gimnasio_id="mock-gym",
        notas="Limpieza profunda de tapizado y estructura.",
        realizado_por_id="u-gim-001",
        realizado_por_nombre="Admin Gimnasio",
        origen="manual",
    ),
    Mantenimiento(
        id="mant-005",
        maquina_id="mq-001",
        maquina_nombre="Press de banca",
        fecha=_hace_dias(45),
        tipo="preventivo",
        gimnasio_id="mock-gym",
        notas="Revisión de banco y barra. Todo en orden.",
        realizado_por_id="u-gim-001",
        realizado_por_nombre="Admin Gimnasio",
        origen="manual",
    ),
]


class MockMantenimientosRepository(MantenimientosRepository):

    def __init__(self):
        self._items: List[Mantenimiento] = deepcopy(_MANTENIMIENTOS_MOCK)

    def _calcular_next_num(self) -> int:
        max_n = 0
        for m in self._items:
            try:
                n = int(m.id.replace("mant-", ""))
                if n > max_n:
                    max_n = n
            except ValueError:
                continue
        return max_n + 1

    def _generar_id(self) -> str:
        return f"mant-{self._calcular_next_num():03d}"

    def crear(self, mantenimiento: Mantenimiento) -> Mantenimiento:
        mantenimiento.id = self._generar_id()
        if not mantenimiento.fecha:
            mantenimiento.fecha = _ahora_iso()
        self._items.append(mantenimiento)
        return mantenimiento

    def find_by_id(self, mantenimiento_id: str) -> Optional[Mantenimiento]:
        for m in self._items:
            if m.id == mantenimiento_id:
                return m
        return None

    def listar_por_maquina(self, maquina_id: str, gimnasio_id: str) -> List[Mantenimiento]:
        result = [m for m in self._items if m.maquina_id == maquina_id and m.gimnasio_id == gimnasio_id]
        result.sort(key=lambda m: m.fecha, reverse=True)
        return result

    def listar_todos(self, gimnasio_id: str) -> List[Mantenimiento]:
        result = [m for m in self._items if m.gimnasio_id == gimnasio_id]
        result.sort(key=lambda m: m.fecha, reverse=True)
        return result

    def ultima_por_maquina(self, maquina_id: str, gimnasio_id: str) -> Optional[Mantenimiento]:
        items = self.listar_por_maquina(maquina_id, gimnasio_id)
        return items[0] if items else None

    def eliminar(self, mantenimiento_id: str) -> bool:
        item = self.find_by_id(mantenimiento_id)
        if not item:
            return False
        self._items.remove(item)
        return True