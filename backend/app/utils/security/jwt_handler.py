"""
Validación de JWT emitidos por Supabase.

Supabase firma los tokens con ES256 (ECDSA) usando una clave asimétrica
rotativa identificada por 'kid'. La clave pública se expone en el JWKS:

    {SUPABASE_URL}/auth/v1/.well-known/jwks.json

Usamos PyJWKClient de PyJWT para:
  - Descargar el JWKS una vez (con cache interno).
  - Elegir la clave pública correcta según el 'kid' del token.
  - Verificar firma y expiración.
"""
from typing import Optional
import jwt
from jwt import PyJWKClient
from flask import current_app

from app.errors import AuthError


# Cache de clientes por URL de JWKS. Se inicializa en el primer uso.
_jwk_clients: dict[str, PyJWKClient] = {}


def _get_jwk_client() -> PyJWKClient:
    url = current_app.config.get("SUPABASE_JWKS_URL")
    if not url:
        raise AuthError(
            500,
            "ServerMisconfigured",
            "El servidor no tiene configurado SUPABASE_URL.",
        )
    client = _jwk_clients.get(url)
    if client is None:
        client = PyJWKClient(url, cache_keys=True, lifespan=3600)
        _jwk_clients[url] = client
    return client


def decodificar_token(token: str) -> dict:
    """
    Decodifica y valida un JWT de Supabase contra su JWKS público.
    Lanza AuthError si es inválido o expiró.
    """
    try:
        client = _get_jwk_client()
        signing_key = client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256", "RS256", "HS256"],
            options={"verify_aud": False},
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthError(401, "TokenExpired", "El token expiró.")
    except jwt.InvalidTokenError as e:
        raise AuthError(401, "InvalidToken", f"Token inválido: {e}")
    except Exception as e:
        raise AuthError(401, "InvalidToken", f"Token inválido: {e}")


def extraer_token_de_header(header_value: Optional[str]) -> str:
    """Extrae el token de un header 'Authorization: Bearer <token>'."""
    if not header_value:
        raise AuthError(401, "MissingToken", "Falta el header Authorization.")
    parts = header_value.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthError(401, "InvalidAuthHeader", "Formato de Authorization inválido.")
    return parts[1]


def extraer_rol_del_payload(payload: dict) -> Optional[str]:
    """Devuelve el rol desde app_metadata del JWT."""
    app_metadata = payload.get("app_metadata") or {}
    return app_metadata.get("rol")