"""
Lógica de negocio del módulo auth.

Con Supabase Auth:
  - Login / registro / logout los maneja el frontend con @supabase/supabase-js.
  - Este módulo ya no emite ni valida credenciales.
  - El endpoint /me devuelve el perfil del usuario autenticado (útil para
    restaurar sesión en el frontend sin pegarle a Supabase).
"""
from typing import Optional
from app.domain.models import Usuario
from app.repositories.supabase_usuarios import SupabaseUsuariosRepository


_repo = SupabaseUsuariosRepository()


def obtener_perfil_actual(usuario: Usuario) -> dict:
    """
    Devuelve el perfil del usuario autenticado, filtrado por su propio rol.
    Un alumno nunca recibe sus notas_profesor.
    """
    return usuario.to_public_dict_for(usuario.rol)


def buscar_por_email(email: str) -> Optional[Usuario]:
    """Helper para casos puntuales (no expuesto como endpoint)."""
    return _repo.find_by_email(email)