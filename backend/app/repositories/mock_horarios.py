"""
Implementación mock del repositorio de horarios.
"""
from copy import deepcopy
from datetime import datetime, timezone
from typing import List, Optional
from app.domain.models import Horario
from app.repositories.horarios_repository import HorariosRepository


def _ahora_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _minutos(hhmm: str) -> int:
    """Convierte 'HH:MM' a minutos desde las 00:00. Para comparar y detectar solapamientos."""
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def _solapan(inicio_a: str, fin_a: str, inicio_b: str, fin_b: str) -> bool:
    """True si dos rangos [inicio, fin) se superponen."""
    a_start = _minutos(inicio_a)
    a_end = _minutos(fin_a)
    b_start = _minutos(inicio_b)
    b_end = _minutos(fin_b)
    return a_start < b_end and b_start < a_end


_HORARIOS_MOCK: List[Horario] = [
    Horario(
        id="hor-001",
        profesor_id="u-pro-001",
        profesor_nombre="Prof. Martínez",
        gimnasio_id="mock-gym",
        dia_semana=0,             # lunes
        hora_inicio="08:00",
        hora_fin="12:00",
        notas="Turno mañana",
        fecha_creacion=_ahora_iso(),
    ),
    Horario(
        id="hor-002",
        profesor_id="u-pro-001",
        profesor_nombre="Prof. Martínez",
        gimnasio_id="mock-gym",
        dia_semana=2,             # miércoles
        hora_inicio="17:00",
        hora_fin="21:00",
        notas="Turno tarde",
        fecha_creacion=_ahora_iso(),
    ),
    Horario(
        id="hor-003",
        profesor_id="u-pro-001",
        profesor_nombre="Prof. Martínez",
        gimnasio_id="mock-gym",
        dia_semana=4,             # viernes
        hora_inicio="08:00",
        hora_fin="12:00",
        notas="Turno mañana",
        fecha_creacion=_ahora_iso(),
    ),
    Horario(
        id="hor-004",
        profesor_id="u-gim-001",
        profesor_nombre="Admin Gimnasio",
        gimnasio_id="mock-gym",
        dia_semana=1,             # martes
        hora_inicio="10:00",
        hora_fin="14:00",
        notas="Clase funcional",
        fecha_creacion=_ahora_iso(),
    ),
]


class MockHorariosRepository(HorariosRepository):

    def __init__(self):
        self._horarios: List[Horario] = deepcopy(_HORARIOS_MOCK)

    def _calcular_next_num(self) -> int:
        max_n = 0
        for h in self._horarios:
            try:
                n = int(h.id.replace("hor-", ""))
                if n > max_n:
                    max_n = n
            except ValueError:
                continue
        return max_n + 1

    def _generar_id(self) -> str:
        return f"hor-{self._calcular_next_num():03d}"

    def listar(self, gimnasio_id: str, profesor_id: Optional[str] = None) -> List[Horario]:
        horarios = [h for h in self._horarios if h.gimnasio_id == gimnasio_id]
        if profesor_id:
            return [h for h in horarios if h.profesor_id == profesor_id]
        return horarios

    def find_by_id(self, horario_id: str) -> Optional[Horario]:
        for h in self._horarios:
            if h.id == horario_id:
                return h
        return None

    def crear(self, horario: Horario) -> Horario:
        horario.id = self._generar_id()
        horario.fecha_creacion = _ahora_iso()
        self._horarios.append(horario)
        return horario

    def actualizar(self, horario_id: str, data: dict) -> Optional[Horario]:
        horario = self.find_by_id(horario_id)
        if not horario:
            return None
        if "dia_semana" in data:
            horario.dia_semana = data["dia_semana"]
        if "hora_inicio" in data:
            horario.hora_inicio = data["hora_inicio"]
        if "hora_fin" in data:
            horario.hora_fin = data["hora_fin"]
        if "notas" in data:
            horario.notas = data["notas"]
        return horario

    def eliminar(self, horario_id: str) -> bool:
        horario = self.find_by_id(horario_id)
        if not horario:
            return False
        self._horarios.remove(horario)
        return True

    def hay_solapamiento(
        self,
        profesor_id: str,
        dia_semana: int,
        hora_inicio: str,
        hora_fin: str,
        excluir_id: Optional[str] = None,
    ) -> bool:
        for h in self._horarios:
            if h.profesor_id != profesor_id:
                continue
            if h.dia_semana != dia_semana:
                continue
            if excluir_id and h.id == excluir_id:
                continue
            if _solapan(hora_inicio, hora_fin, h.hora_inicio, h.hora_fin):
                return True
        return False