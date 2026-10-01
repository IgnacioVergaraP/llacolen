"""Lógica de negocio del módulo maquinas."""
from typing import List
from app.errors import AuthError
from app.domain.models import Maquina
from app.repositories.mock_maquinas import MockMaquinasRepository


_repo = MockMaquinasRepository()


def listar_maquinas(musculo: str | None = None) -> List[dict]:
    """Devuelve todas las máquinas o filtradas por grupo muscular."""
    maquinas = (
        _repo.listar_por_musculo(musculo) if musculo else _repo.listar()
    )
    return [m.to_dict() for m in maquinas]


def obtener_maquina(maquina_id: str) -> dict:
    """Devuelve el detalle de una máquina o lanza 404."""
    maquina = _repo.find_by_id(maquina_id)
    if not maquina:
        raise AuthError(404, "NotFound", f"No existe una máquina con id '{maquina_id}'.")
    return maquina.to_dict()