"""
Implementación del repositorio de solicitudes de rutina contra Supabase.
"""
from datetime import datetime, timezone
from typing import List, Optional
from app.domain.models import SolicitudRutina
from app.repositories.solicitudes_rutina_repository import SolicitudesRutinaRepository
from app.extensions import get_supabase


_COLUMNS = (
    "id,estado,alumno_id,alumno_nombre,objetivo,dias_por_semana,"
    "comentarios,grupos_interes,"
    "profesor_preferido_id,profesor_preferido_nombre,"
    "profesor_id,profesor_nombre,"
    "rutina_id,mensaje_resolucion,motivo_rechazo,"
    "estado_liberacion,fecha_liberacion_solicitada,"
    "liberacion_revisada_por_id,liberacion_revisada_por_nombre,liberacion_motivo_rechazo,"
    "fecha_creacion,fecha_tomada,fecha_revision,gimnasio_id"
)


def _row_a_solicitud(row: dict) -> SolicitudRutina:
    fecha_cre = row.get("fecha_creacion")
    fecha_tom = row.get("fecha_tomada")
    fecha_rev = row.get("fecha_revision")
    fecha_lib = row.get("fecha_liberacion_solicitada")

    def _iso(v):
        return v.isoformat() if hasattr(v, "isoformat") else v

    return SolicitudRutina(
        id=row["id"],
        estado=row["estado"],
        alumno_id=row["alumno_id"],
        alumno_nombre=row["alumno_nombre"],
        objetivo=row["objetivo"],
        dias_por_semana=row["dias_por_semana"],
        comentarios=row.get("comentarios"),
        grupos_interes=list(row["grupos_interes"]) if row.get("grupos_interes") else None,
        profesor_preferido_id=row.get("profesor_preferido_id"),
        profesor_preferido_nombre=row.get("profesor_preferido_nombre"),
        profesor_id=row.get("profesor_id"),
        profesor_nombre=row.get("profesor_nombre"),
        rutina_id=row.get("rutina_id"),
        mensaje_resolucion=row.get("mensaje_resolucion"),
        motivo_rechazo=row.get("motivo_rechazo"),
        estado_liberacion=row.get("estado_liberacion"),
        fecha_liberacion_solicitada=_iso(fecha_lib),
        liberacion_revisada_por_id=row.get("liberacion_revisada_por_id"),
        liberacion_revisada_por_nombre=row.get("liberacion_revisada_por_nombre"),
        liberacion_motivo_rechazo=row.get("liberacion_motivo_rechazo"),
        fecha_creacion=_iso(fecha_cre),
        fecha_tomada=_iso(fecha_tom),
        fecha_revision=_iso(fecha_rev),
        gimnasio_id=row["gimnasio_id"],
    )


class SupabaseSolicitudesRutinaRepository(SolicitudesRutinaRepository):

    def __init__(self):
        self._sb = get_supabase()

    def crear(self, solicitud: SolicitudRutina) -> SolicitudRutina:
        payload = {
            "estado": solicitud.estado,
            "alumno_id": solicitud.alumno_id,
            "alumno_nombre": solicitud.alumno_nombre,
            "objetivo": solicitud.objetivo,
            "dias_por_semana": solicitud.dias_por_semana,
            "comentarios": solicitud.comentarios,
            "grupos_interes": list(solicitud.grupos_interes) if solicitud.grupos_interes else [],
            "profesor_preferido_id": solicitud.profesor_preferido_id,
            "profesor_preferido_nombre": solicitud.profesor_preferido_nombre,
            "gimnasio_id": solicitud.gimnasio_id,
        }
        resp = self._sb.table("solicitudes_rutina").insert(payload).execute()
        if not resp.data:
            raise RuntimeError("No se pudo crear la solicitud de rutina.")
        return _row_a_solicitud(resp.data[0])

    def find_by_id(self, solicitud_id: str) -> Optional[SolicitudRutina]:
        resp = (
            self._sb.table("solicitudes_rutina")
            .select(_COLUMNS)
            .eq("id", solicitud_id)
            .limit(1)
            .execute()
        )
        if not resp.data:
            return None
        return _row_a_solicitud(resp.data[0])

    def listar_por_alumno(self, alumno_id: str) -> List[SolicitudRutina]:
        resp = (
            self._sb.table("solicitudes_rutina")
            .select(_COLUMNS)
            .eq("alumno_id", alumno_id)
            .order("fecha_creacion", desc=True)
            .execute()
        )
        return [_row_a_solicitud(row) for row in (resp.data or [])]

    def listar_todas(self, gimnasio_id: str) -> List[SolicitudRutina]:
        resp = (
            self._sb.table("solicitudes_rutina")
            .select(_COLUMNS)
            .eq("gimnasio_id", gimnasio_id)
            .order("fecha_creacion", desc=True)
            .execute()
        )
        return [_row_a_solicitud(row) for row in (resp.data or [])]

    def listar_pendientes(self, gimnasio_id: str) -> List[SolicitudRutina]:
        resp = (
            self._sb.table("solicitudes_rutina")
            .select(_COLUMNS)
            .eq("estado", "pendiente")
            .eq("gimnasio_id", gimnasio_id)
            .order("fecha_creacion", desc=False)
            .execute()
        )
        return [_row_a_solicitud(row) for row in (resp.data or [])]

    def listar_por_profesor(self, profesor_id: str) -> List[SolicitudRutina]:
        resp = (
            self._sb.table("solicitudes_rutina")
            .select(_COLUMNS)
            .eq("profesor_id", profesor_id)
            .order("fecha_creacion", desc=True)
            .execute()
        )
        return [_row_a_solicitud(row) for row in (resp.data or [])]

    def actualizar(self, solicitud_id: str, data: dict) -> Optional[SolicitudRutina]:
        """
        Actualiza una solicitud. Se usa para:
          - Alumno cancela
          - Profesor toma / resuelve / rechaza / pide liberación
          - Admin aprueba / rechaza liberación
        """
        payload = dict(data)
        # Normalizar nombres de campo `grupos_interes` si vienen como `grupos_interes`
        if "grupos_interes" in payload and payload["grupos_interes"] is not None:
            payload["grupos_interes"] = list(payload["grupos_interes"])

        resp = (
            self._sb.table("solicitudes_rutina")
            .update(payload)
            .eq("id", solicitud_id)
            .execute()
        )
        if not resp.data:
            return None
        return _row_a_solicitud(resp.data[0])