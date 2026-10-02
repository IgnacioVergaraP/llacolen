"""
Implementación del repositorio de reportes contra Supabase.
"""
from datetime import datetime, timezone
from typing import List, Optional
from app.domain.models import Reporte
from app.repositories.reportes_repository import ReportesRepository
from app.extensions import get_supabase


_COLUMNS = (
    "id,estado,tipo,prioridad,descripcion,"
    "reportante_id,reportante_nombre,"
    "maquina_id,maquina_nombre,foto_url,"
    "resolucion,revisado_por_id,revisado_por_nombre,"
    "fecha_creacion,fecha_revision"
)


def _row_a_reporte(row: dict) -> Reporte:
    fecha_cre = row.get("fecha_creacion")
    fecha_rev = row.get("fecha_revision")
    return Reporte(
        id=row["id"],
        estado=row["estado"],
        tipo=row["tipo"],
        prioridad=row["prioridad"],
        descripcion=row.get("descripcion", ""),
        reportante_id=row["reportante_id"],
        reportante_nombre=row["reportante_nombre"],
        maquina_id=row.get("maquina_id"),
        maquina_nombre=row.get("maquina_nombre"),
        foto_url=row.get("foto_url"),
        resolucion=row.get("resolucion"),
        revisado_por_id=row.get("revisado_por_id"),
        revisado_por_nombre=row.get("revisado_por_nombre"),
        fecha_creacion=fecha_cre.isoformat() if hasattr(fecha_cre, "isoformat") else (fecha_cre or ""),
        fecha_revision=fecha_rev.isoformat() if hasattr(fecha_rev, "isoformat") else fecha_rev,
    )


class SupabaseReportesRepository(ReportesRepository):

    def __init__(self):
        self._sb = get_supabase()

    def crear(self, reporte: Reporte) -> Reporte:
        payload = {
            "estado": reporte.estado,
            "tipo": reporte.tipo,
            "prioridad": reporte.prioridad,
            "descripcion": reporte.descripcion,
            "reportante_id": reporte.reportante_id,
            "reportante_nombre": reporte.reportante_nombre,
            "maquina_id": reporte.maquina_id,
            "maquina_nombre": reporte.maquina_nombre,
            "foto_url": reporte.foto_url,
        }
        resp = self._sb.table("reportes").insert(payload).execute()
        if not resp.data:
            raise RuntimeError("No se pudo crear el reporte.")
        return _row_a_reporte(resp.data[0])

    def find_by_id(self, reporte_id: str) -> Optional[Reporte]:
        resp = (
            self._sb.table("reportes")
            .select(_COLUMNS)
            .eq("id", reporte_id)
            .limit(1)
            .execute()
        )
        if not resp.data:
            return None
        return _row_a_reporte(resp.data[0])

    def listar_por_reportante(self, reportante_id: str) -> List[Reporte]:
        resp = (
            self._sb.table("reportes")
            .select(_COLUMNS)
            .eq("reportante_id", reportante_id)
            .order("fecha_creacion", desc=True)
            .execute()
        )
        return [_row_a_reporte(row) for row in (resp.data or [])]

    def listar_todos(self) -> List[Reporte]:
        resp = (
            self._sb.table("reportes")
            .select(_COLUMNS)
            .order("fecha_creacion", desc=True)
            .execute()
        )
        return [_row_a_reporte(row) for row in (resp.data or [])]

    def actualizar(self, reporte_id: str, data: dict) -> Optional[Reporte]:
        """
        Actualiza un reporte. Se usa para:
          - Cancelar (estado='cancelado')
          - Marcar en revisión (estado='en_revision', revisado_por_*)
          - Resolver (estado='resuelto', resolucion, revisado_por_*)
        """
        payload = dict(data)
        if "estado" in payload and "fecha_revision" not in payload:
            payload["fecha_revision"] = datetime.now(timezone.utc).isoformat()

        resp = (
            self._sb.table("reportes")
            .update(payload)
            .eq("id", reporte_id)
            .execute()
        )
        if not resp.data:
            return None
        return _row_a_reporte(resp.data[0])