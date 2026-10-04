"""
Implementación del repositorio de mantenciones contra Supabase.
"""
from datetime import datetime, timezone
from typing import List, Optional
from app.domain.models import Mantenimiento
from app.repositories.mantenimientos_repository import MantenimientosRepository
from app.extensions import get_supabase


_COLUMNS = (
    "id,maquina_id,maquina_nombre,fecha,tipo,notas,"
    "realizado_por_id,realizado_por_nombre,origen,reporte_id,gimnasio_id"
)


def _row_a_mantenimiento(row: dict) -> Mantenimiento:
    fecha = row.get("fecha")
    return Mantenimiento(
        id=row["id"],
        maquina_id=row["maquina_id"],
        maquina_nombre=row["maquina_nombre"],
        fecha=fecha.isoformat() if hasattr(fecha, "isoformat") else (fecha or ""),
        tipo=row["tipo"],
        notas=row.get("notas"),
        realizado_por_id=row.get("realizado_por_id"),
        realizado_por_nombre=row.get("realizado_por_nombre"),
        origen=row.get("origen", "manual"),
        reporte_id=row.get("reporte_id"),
        gimnasio_id=row.get("gimnasio_id"),
    )


class SupabaseMantenimientosRepository(MantenimientosRepository):

    def __init__(self):
        self._sb = get_supabase()

    def crear(self, mantenimiento: Mantenimiento) -> Mantenimiento:
        payload = {
            "maquina_id": mantenimiento.maquina_id,
            "maquina_nombre": mantenimiento.maquina_nombre,
            "fecha": mantenimiento.fecha or datetime.now(timezone.utc).isoformat(),
            "tipo": mantenimiento.tipo,
            "notas": mantenimiento.notas,
            "realizado_por_id": mantenimiento.realizado_por_id,
            "realizado_por_nombre": mantenimiento.realizado_por_nombre,
            "origen": mantenimiento.origen,
            "reporte_id": mantenimiento.reporte_id,
            "gimnasio_id": mantenimiento.gimnasio_id,
        }
        resp = self._sb.table("mantenciones").insert(payload).execute()
        if not resp.data:
            raise RuntimeError("No se pudo crear la mantención.")
        return _row_a_mantenimiento(resp.data[0])

    def find_by_id(self, mantenimiento_id: str) -> Optional[Mantenimiento]:
        resp = (
            self._sb.table("mantenciones")
            .select(_COLUMNS)
            .eq("id", mantenimiento_id)
            .limit(1)
            .execute()
        )
        if not resp.data:
            return None
        return _row_a_mantenimiento(resp.data[0])

    def listar_por_maquina(self, maquina_id: str, gimnasio_id: str) -> List[Mantenimiento]:
        resp = (
            self._sb.table("mantenciones")
            .select(_COLUMNS)
            .eq("maquina_id", maquina_id)
            .eq("gimnasio_id", gimnasio_id)
            .order("fecha", desc=True)
            .execute()
        )
        return [_row_a_mantenimiento(row) for row in (resp.data or [])]

    def listar_todos(self, gimnasio_id: str) -> List[Mantenimiento]:
        resp = (
            self._sb.table("mantenciones")
            .select(_COLUMNS)
            .eq("gimnasio_id", gimnasio_id)
            .order("fecha", desc=True)
            .execute()
        )
        return [_row_a_mantenimiento(row) for row in (resp.data or [])]

    def ultima_por_maquina(self, maquina_id: str, gimnasio_id: str) -> Optional[Mantenimiento]:
        items = self.listar_por_maquina(maquina_id, gimnasio_id)
        return items[0] if items else None

    def eliminar(self, mantenimiento_id: str) -> bool:
        resp = (
            self._sb.table("mantenciones")
            .delete()
            .eq("id", mantenimiento_id)
            .execute()
        )
        return bool(resp.data)