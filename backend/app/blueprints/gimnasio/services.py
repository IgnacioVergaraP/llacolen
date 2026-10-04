"""Lógica de negocio del módulo gimnasio (config visual)."""
from app.errors import AuthError
from app.repositories.supabase_gimnasios import SupabaseGimnasiosRepository


_repo = SupabaseGimnasiosRepository()


def obtener_config(gimnasio_id: str) -> dict:
    gimnasio = _repo.find_by_id(gimnasio_id)
    if not gimnasio:
        raise AuthError(404, "NotFound", f"No existe un gimnasio con id '{gimnasio_id}'.")
    return gimnasio.to_dict()