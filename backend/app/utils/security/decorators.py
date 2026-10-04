"""
Decoradores de autenticación y autorización basados en Supabase Auth.

@requiere_auth:
    Valida el JWT de Supabase. Inyecta g.usuario_actual (Usuario del perfil)
    y g.jwt_payload (payload completo).

@requiere_rol(*roles):
    Además de autenticar, exige que el rol del usuario esté entre los permitidos.
    El rol se lee de app_metadata del JWT.
"""
from functools import wraps
from flask import request, g

from app.errors import AuthError
from app.utils.security.jwt_handler import (
    decodificar_token,
    extraer_token_de_header,
    extraer_rol_del_payload,
)
from app.repositories.supabase_usuarios import SupabaseUsuariosRepository


def _get_repo() -> SupabaseUsuariosRepository:
    return SupabaseUsuariosRepository()


def requiere_auth(fn):
    """Exige un JWT válido. Deja el Usuario en g.usuario_actual."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization")
        token = extraer_token_de_header(header)
        payload = decodificar_token(token)

        user_id = payload.get("sub")
        if not user_id:
            raise AuthError(401, "InvalidToken", "El token no tiene 'sub'.")

        repo = _get_repo()
        usuario = repo.find_by_id(user_id)
        if not usuario or not usuario.activo:
            raise AuthError(401, "UserNotFound", "Usuario no encontrado o inactivo.")

        g.usuario_actual = usuario
        g.jwt_payload = payload
        g.gimnasio_id = usuario.gimnasio_id
        return fn(*args, **kwargs)
    return wrapper


def requiere_rol(*roles_permitidos: str):
    """Exige JWT válido + rol permitido (desde app_metadata del JWT)."""
    def decorator(fn):
        @wraps(fn)
        @requiere_auth
        def wrapper(*args, **kwargs):
            payload = g.jwt_payload
            rol = extraer_rol_del_payload(payload)

            if rol not in roles_permitidos:
                raise AuthError(
                    403,
                    "Forbidden",
                    f"Rol '{rol}' no autorizado para este recurso.",
                )
            return fn(*args, **kwargs)
        return wrapper
    return decorator