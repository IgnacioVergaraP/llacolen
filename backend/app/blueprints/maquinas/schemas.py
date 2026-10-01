"""Validación de parámetros del módulo maquinas."""
from app.errors import AuthError


def validar_query_musculo(raw) -> str | None:
    """
    Normaliza el query param 'musculo'. Devuelve None si no vino,
    o el string en minúsculas si es válido.
    """
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise AuthError(400, "InvalidQuery", "El parámetro 'musculo' debe ser texto.")
    value = raw.strip().lower()
    if not value:
        return None
    if len(value) > 40:
        raise AuthError(400, "InvalidQuery", "El parámetro 'musculo' es demasiado largo.")
    return value