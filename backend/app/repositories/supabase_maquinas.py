"""Implementación del repositorio de máquinas contra Supabase."""
from typing import List, Optional
from app.domain.models import Maquina
from app.repositories.maquinas_repository import MaquinasRepository
from app.extensions import get_supabase


_COLUMNS = "id,nombre,grupos_musculares,descripcion,video_url,imagen_url,gimnasio_id"


def _row_a_maquina(row: dict) -> Maquina:
    return Maquina(
        id=row["id"],
        nombre=row["nombre"],
        grupos_musculares=list(row.get("grupos_musculares") or []),
        descripcion=row.get("descripcion", ""),
        video_url=row.get("video_url", ""),
        imagen_url=row.get("imagen_url", ""),
        gimnasio_id=row["gimnasio_id"],
    )


class SupabaseMaquinasRepository(MaquinasRepository):

    def __init__(self):
        self._sb = get_supabase()

    def listar(self, gimnasio_id: str) -> List[Maquina]:
        resp = (
            self._sb.table("maquinas")
            .select(_COLUMNS)
            .eq("gimnasio_id", gimnasio_id)
            .order("nombre")
            .execute()
        )
        return [_row_a_maquina(row) for row in (resp.data or [])]

    def listar_por_musculo(self, musculo: str, gimnasio_id: str) -> List[Maquina]:
        musculo = musculo.strip().lower()
        resp = (
            self._sb.table("maquinas")
            .select(_COLUMNS)
            .eq("gimnasio_id", gimnasio_id)
            .contains("grupos_musculares", [musculo])
            .order("nombre")
            .execute()
        )
        return [_row_a_maquina(row) for row in (resp.data or [])]

    def find_by_id(self, maquina_id: str, gimnasio_id: Optional[str] = None) -> Optional[Maquina]:
        query = (
            self._sb.table("maquinas")
            .select(_COLUMNS)
            .eq("id", maquina_id)
        )
        if gimnasio_id is not None:
            query = query.eq("gimnasio_id", gimnasio_id)
        resp = query.limit(1).execute()
        if not resp.data:
            return None
        return _row_a_maquina(resp.data[0])

    def crear(
        self,
        nombre: str,
        grupos_musculares: List[str],
        descripcion: str,
        video_url: str,
        gimnasio_id: str,
        imagen_url: str = "",
    ) -> Maquina:
        payload = {
            "nombre": nombre,
            "grupos_musculares": list(grupos_musculares),
            "descripcion": descripcion,
            "video_url": video_url,
            "imagen_url": imagen_url,
            "gimnasio_id": gimnasio_id,
        }
        resp = self._sb.table("maquinas").insert(payload).execute()
        if not resp.data:
            raise RuntimeError("No se pudo crear la máquina.")
        return _row_a_maquina(resp.data[0])