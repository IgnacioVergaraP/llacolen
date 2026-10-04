"""
Implementación del repositorio de horarios contra Supabase.
"""
from datetime import datetime, timezone
from typing import List, Optional
from app.domain.models import Horario
from app.repositories.horarios_repository import HorariosRepository
from app.extensions import get_supabase


_COLUMNS = "id,profesor_id,profesor_nombre,dia_semana,hora_inicio,hora_fin,notas,fecha_creacion,gimnasio_id"


def _row_a_horario(row: dict) -> Horario:
    fecha_cre = row.get("fecha_creacion")
    return Horario(
        id=row["id"],
        profesor_id=row["profesor_id"],
        profesor_nombre=row["profesor_nombre"],
        dia_semana=row["dia_semana"],
        hora_inicio=row["hora_inicio"],
        hora_fin=row["hora_fin"],
        notas=row.get("notas"),
        fecha_creacion=fecha_cre.isoformat() if hasattr(fecha_cre, "isoformat") else (fecha_cre or ""),
        gimnasio_id=row["gimnasio_id"],
    )


def _minutos(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def _solapan(inicio_a: str, fin_a: str, inicio_b: str, fin_b: str) -> bool:
    a_start = _minutos(inicio_a)
    a_end = _minutos(fin_a)
    b_start = _minutos(inicio_b)
    b_end = _minutos(fin_b)
    return a_start < b_end and b_start < a_end


class SupabaseHorariosRepository(HorariosRepository):

    def __init__(self):
        self._sb = get_supabase()

    def listar(self, gimnasio_id: str, profesor_id: Optional[str] = None) -> List[Horario]:
        query = (
            self._sb.table("horarios")
            .select(_COLUMNS)
        )
        query = query.eq("gimnasio_id", gimnasio_id)
        if profesor_id:
            query = query.eq("profesor_id", profesor_id)
        resp = query.order("dia_semana").order("hora_inicio").execute()
        return [_row_a_horario(row) for row in (resp.data or [])]

    def find_by_id(self, horario_id: str) -> Optional[Horario]:
        resp = (
            self._sb.table("horarios")
            .select(_COLUMNS)
            .eq("id", horario_id)
            .limit(1)
            .execute()
        )
        if not resp.data:
            return None
        return _row_a_horario(resp.data[0])

    def crear(self, horario: Horario) -> Horario:
        payload = {
            "profesor_id": horario.profesor_id,
            "profesor_nombre": horario.profesor_nombre,
            "dia_semana": horario.dia_semana,
            "hora_inicio": horario.hora_inicio,
            "hora_fin": horario.hora_fin,
            "notas": horario.notas,
            "gimnasio_id": horario.gimnasio_id,
        }
        resp = self._sb.table("horarios").insert(payload).execute()
        if not resp.data:
            raise RuntimeError("No se pudo crear el horario.")
        return _row_a_horario(resp.data[0])

    def actualizar(self, horario_id: str, data: dict) -> Optional[Horario]:
        resp = (
            self._sb.table("horarios")
            .update(data)
            .eq("id", horario_id)
            .execute()
        )
        if not resp.data:
            return None
        return _row_a_horario(resp.data[0])

    def eliminar(self, horario_id: str) -> bool:
        resp = (
            self._sb.table("horarios")
            .delete()
            .eq("id", horario_id)
            .execute()
        )
        return bool(resp.data)

    def hay_solapamiento(
        self,
        profesor_id: str,
        dia_semana: int,
        hora_inicio: str,
        hora_fin: str,
        excluir_id: Optional[str] = None,
    ) -> bool:
        # Traemos los horarios del profesor para ese día y chequeamos en Python.
        # RLS no permite hacer range queries complejas sobre text sin índices btree
        # con operadores específicos, y el volumen es chico.
        query = (
            self._sb.table("horarios")
            .select(_COLUMNS)
            .eq("profesor_id", profesor_id)
            .eq("dia_semana", dia_semana)
        )
        if excluir_id:
            query = query.neq("id", excluir_id)

        resp = query.execute()
        for row in (resp.data or []):
            if _solapan(hora_inicio, hora_fin, row["hora_inicio"], row["hora_fin"]):
                return True
        return False