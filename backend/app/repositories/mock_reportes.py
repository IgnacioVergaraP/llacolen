"""
Implementación mock del repositorio de reportes.
"""
from copy import deepcopy
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from app.domain.models import Reporte
from app.repositories.reportes_repository import ReportesRepository


def _ahora_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hace_dias(dias: int) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=dias)
    return dt.isoformat()


# Un reporte de ejemplo precargado para que la pantalla no esté vacía.
_REPORTES_INICIALES: List[Reporte] = [
    Reporte(
        id="rep-0001",
        estado="abierto",
        tipo="rota",
        prioridad="alta",
        descripcion="La polea del jalón al pecho hace un ruido fuerte y se traba al subir. Puede lastimar a alguien.",
        reportante_id="u-pro-001",
        reportante_nombre="Prof. Martínez",
        gimnasio_id="mock-gym",
        maquina_id="mq-004",
        maquina_nombre="Jalón al pecho en polea",
        fecha_creacion=_hace_dias(1),
    ),
    Reporte(
        id="rep-0002",
        estado="resuelto",
        tipo="falta_accesorio",
        prioridad="media",
        descripcion="Falta el agarre de la mancuerna del curl de bíceps.",
        reportante_id="u-pro-001",
        reportante_nombre="Prof. Martínez",
        gimnasio_id="mock-gym",
        maquina_id="mq-009",
        maquina_nombre="Curl de bíceps con mancuernas",
        resolucion="Se repuso el agarre faltante.",
        revisado_por_id="u-gim-001",
        revisado_por_nombre="Admin Gimnasio",
        fecha_creacion=_hace_dias(5),
        fecha_revision=_hace_dias(4),
    ),
]


class MockReportesRepository(ReportesRepository):

    def __init__(self):
        self._reportes: List[Reporte] = deepcopy(_REPORTES_INICIALES)

    def _calcular_next_num(self) -> int:
        max_n = 0
        for r in self._reportes:
            try:
                n = int(r.id.replace("rep-", ""))
                if n > max_n:
                    max_n = n
            except ValueError:
                continue
        return max_n + 1

    def _generar_id(self) -> str:
        return f"rep-{self._calcular_next_num():04d}"

    def crear(self, reporte: Reporte) -> Reporte:
        reporte.id = self._generar_id()
        reporte.fecha_creacion = _ahora_iso()
        self._reportes.append(reporte)
        return reporte

    def find_by_id(self, reporte_id: str) -> Optional[Reporte]:
        for r in self._reportes:
            if r.id == reporte_id:
                return r
        return None

    def listar_por_reportante(self, reportante_id: str) -> List[Reporte]:
        result = [r for r in self._reportes if r.reportante_id == reportante_id]
        result.sort(key=lambda r: r.fecha_creacion, reverse=True)
        return result

    def listar_todos(self, gimnasio_id: str) -> List[Reporte]:
        result = [r for r in self._reportes if r.gimnasio_id == gimnasio_id]
        result.sort(key=lambda r: r.fecha_creacion, reverse=True)
        return result
    
    def actualizar(self, reporte_id: str, data: dict) -> Optional[Reporte]:
        reporte = self.find_by_id(reporte_id)
        if not reporte:
            return None
        for key, value in data.items():
            if hasattr(reporte, key):
                setattr(reporte, key, value)
        return reporte