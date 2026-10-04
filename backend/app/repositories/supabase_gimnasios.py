"""
Implementación del repositorio de gimnasios contra Supabase.
"""
from typing import Optional
from app.domain.models import Gimnasio
from app.repositories.gimnasios_repository import GimnasiosRepository
from app.extensions import get_supabase


_COLUMNS = "id,nombre,slug,logo_url,color_primario,tabs_habilitadas,activo,fecha_creacion"


def _row_a_gimnasio(row: dict) -> Gimnasio:
    fecha = row.get("fecha_creacion")
    return Gimnasio(
        id=row["id"],
        nombre=row["nombre"],
        slug=row["slug"],
        color_primario=row.get("color_primario", "#2f6f4e"),
        logo_url=row.get("logo_url"),
        tabs_habilitadas=list(row["tabs_habilitadas"]) if row.get("tabs_habilitadas") else [],
        activo=row.get("activo", True),
        fecha_creacion=fecha.isoformat() if hasattr(fecha, "isoformat") else fecha,
    )


class SupabaseGimnasiosRepository(GimnasiosRepository):

    def __init__(self):
        self._sb = get_supabase()

    def find_by_id(self, gimnasio_id: str) -> Optional[Gimnasio]:
        resp = (
            self._sb.table("gimnasios")
            .select(_COLUMNS)
            .eq("id", gimnasio_id)
            .limit(1)
            .execute()
        )
        if not resp.data:
            return None
        return _row_a_gimnasio(resp.data[0])

    def find_by_slug(self, slug: str) -> Optional[Gimnasio]:
        resp = (
            self._sb.table("gimnasios")
            .select(_COLUMNS)
            .eq("slug", slug)
            .limit(1)
            .execute()
        )
        if not resp.data:
            return None
        return _row_a_gimnasio(resp.data[0])