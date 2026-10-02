"""
Implementación del repositorio de máquinas contra Supabase (tabla public.maquinas).

El backend usa el service_role key, así que ignora RLS. Las reglas de negocio
se aplican en la capa de services.
"""
from typing import List, Optional
from app.domain.models import Maquina
from app.repositories.maquinas_repository import MaquinasRepository
from app.extensions import get_supabase


_COLUMNS = "id,nombre,grupos_musculares,descripcion,video_url,imagen_url"


def _row_a_maquina(row: dict) -> Maquina:
    return Maquina(
        id=row["id"],
        nombre=row["nombre"],
        grupos_musculares=list(row.get("grupos_musculares") or []),
        descripcion=row.get("descripcion", ""),
        video_url=row.get("video_url", ""),
        imagen_url=row.get("imagen_url", ""),
    )


class SupabaseMaquinasRepository(MaquinasRepository):

    def __init__(self):
        self._sb = get_supabase()

    def listar(self) -> List[Maquina]:
        resp = (
            self._sb.table("maquinas")
            .select(_COLUMNS)
            .order("nombre")
            .execute()
        )
        return [_row_a_maquina(row) for row in (resp.data or [])]

    def listar_por_musculo(self, musculo: str) -> List[Maquina]:
        musculo = musculo.strip().lower()
        # `contains` en el cliente de Supabase traduce a `@>` de Postgres sobre el array
        resp = (
            self._sb.table("maquinas")
            .select(_COLUMNS)
            .contains("grupos_musculares", [musculo])
            .order("nombre")
            .execute()
        )
        return [_row_a_maquina(row) for row in (resp.data or [])]

    def find_by_id(self, maquina_id: str) -> Optional[Maquina]:
        resp = (
            self._sb.table("maquinas")
            .select(_COLUMNS)
            .eq("id", maquina_id)
            .limit(1)
            .execute()
        )
        if not resp.data:
            return None
        return _row_a_maquina(resp.data[0])

    def crear(
        self,
        nombre: str,
        grupos_musculares: List[str],
        descripcion: str,
        video_url: str,
        imagen_url: str = "",
    ) -> Maquina:
        payload = {
            "nombre": nombre,
            "grupos_musculares": list(grupos_musculares),
            "descripcion": descripcion,
            "video_url": video_url,
            "imagen_url": imagen_url,
        }
        resp = self._sb.table("maquinas").insert(payload).execute()
        if not resp.data:
            raise RuntimeError("No se pudo crear la máquina.")
        return _row_a_maquina(resp.data[0])