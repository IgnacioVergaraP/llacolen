"""
Validación de JWT emitidos por Supabase.

Supabase firma los tokens con HS256 usando el JWT Secret del proyecto
(disponible en Settings → API → JWT Settings). Este módulo:
  - Verifica la firma y la expiración.
  - Devuelve el payload decodificado (con 'sub', 'email', 'app_metadata', etc.).
"""
from typing import Optional
import jwt
from flask import current_app

from app.errors import AuthError


def decodificar_token(token: str) -> dict:
    """
    Decodifica y valida un JWT de Supabase. Lanza AuthError si es inválido o expiró.
    """
    secret = current_app.config.get("SUPABASE_JWT_SECRET")
    if not secret:
        raise AuthError(
            500,
            "ServerMisconfigured",
            "El servidor no tiene configurado el JWT secret de Supabase.",
        )

    algorithm = current_app.config.get("SUPABASE_JWT_ALGORITHM", "HS256")

    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=[algorithm],
            # Supabase incluye 'aud' = 'authenticated' para usuarios logueados.
            # No lo exigimos rígidamente para permitir tokens de otros flujos.
            options={"verify_aud": False},
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthError(401, "TokenExpired", "El token expiró.")
    except jwt.InvalidTokenError:
        raise AuthError(401, "InvalidToken", "Token inválido.")


def extraer_token_de_header(header_value: Optional[str]) -> str:
    """Extrae el token de un header 'Authorization: Bearer <token>'."""
    if not header_value:
        raise AuthError(401, "MissingToken", "Falta el header Authorization.")
    parts = header_value.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthError(401, "InvalidAuthHeader", "Formato de Authorization inválido.")
    return parts[1]


def extraer_rol_del_payload(payload: dict) -> Optional[str]:
    """
    Devuelve el rol desde app_metadata del JWT.
    Formato esperado: payload['app_metadata']['rol'].
    """
    app_metadata = payload.get("app_metadata") or {}
    return app_metadata.get("rol")