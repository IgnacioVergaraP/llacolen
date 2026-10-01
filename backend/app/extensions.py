"""
Instancia única del cliente de Supabase para el backend.

Usa el service_role key: esto le da al backend acceso total a la base
de datos ignorando RLS. Es intencional: el backend es el que aplica las
reglas de negocio y decide qué devolver al frontend.

NUNCA exponer el service_role al frontend. El frontend usa su propio
cliente de Supabase con la anon key y está sujeto a RLS.
"""
from supabase import create_client, Client
from app.config import Config


_client: Client | None = None


def get_supabase() -> Client:
    """Devuelve el cliente de Supabase (singleton)."""
    global _client
    if _client is None:
        if not Config.SUPABASE_URL or not Config.SUPABASE_SERVICE_ROLE_KEY:
            raise RuntimeError(
                "Faltan SUPABASE_URL o SUPABASE_SERVICE_ROLE_KEY en el .env"
            )
        _client = create_client(
            Config.SUPABASE_URL,
            Config.SUPABASE_SERVICE_ROLE_KEY,
        )
    return _client