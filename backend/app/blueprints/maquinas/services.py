"""Lógica de negocio del módulo maquinas."""
from typing import List
from app.errors import AuthError
from app.repositories.supabase_maquinas import SupabaseMaquinasRepository


_repo = SupabaseMaquinasRepository()


def listar_maquinas(gimnasio_id: str, musculo: str | None = None) -> List[dict]:
    maquinas = (
        _repo.listar_por_musculo(musculo, gimnasio_id) if musculo
        else _repo.listar(gimnasio_id)
    )
    return [m.to_dict() for m in maquinas]


def obtener_maquina(maquina_id: str, gimnasio_id: str) -> dict:
    maquina = _repo.find_by_id(maquina_id, gimnasio_id)
    if not maquina:
        raise AuthError(404, "NotFound", f"No existe una máquina con id '{maquina_id}'.")
    return maquina.to_dict()