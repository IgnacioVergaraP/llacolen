"""
Implementación del repositorio de usuarios contra Supabase.
"""
from typing import List, Optional
from app.domain.models import Usuario
from app.repositories.usuarios_repository import UsuariosRepository
from app.extensions import get_supabase


_COLUMNS = (
    "id,email,nombre,rol,gimnasio_id,activo,"
    "altura,peso_actual,peso_objetivo,imagen_url,"
    "porcentaje_grasa,fecha_medicion_grasa,origen_grasa,cargado_por_id,"
    "bio,especialidades,anios_experiencia,telefono,"
    "notas_profesor,fecha_alta"
)


def _row_a_usuario(row: dict) -> Usuario:
    fecha = row.get("fecha_alta")
    return Usuario(
        id=row["id"],
        email=row["email"],
        nombre=row["nombre"],
        rol=row["rol"],
        gimnasio_id=row["gimnasio_id"],
        activo=row.get("activo", True),
        altura=float(row["altura"]) if row.get("altura") is not None else None,
        peso_actual=float(row["peso_actual"]) if row.get("peso_actual") is not None else None,
        peso_objetivo=float(row["peso_objetivo"]) if row.get("peso_objetivo") is not None else None,
        imagen_url=row.get("imagen_url"),
        porcentaje_grasa=float(row["porcentaje_grasa"]) if row.get("porcentaje_grasa") is not None else None,
        fecha_medicion_grasa=row.get("fecha_medicion_grasa"),
        origen_grasa=row.get("origen_grasa"),
        cargado_por_id=row.get("cargado_por_id"),
        bio=row.get("bio"),
        especialidades=row.get("especialidades"),
        anios_experiencia=row.get("anios_experiencia"),
        telefono=row.get("telefono"),
        notas_profesor=row.get("notas_profesor"),
        fecha_alta=fecha.isoformat() if hasattr(fecha, "isoformat") else fecha,
    )


class SupabaseUsuariosRepository(UsuariosRepository):

    def __init__(self):
        self._sb = get_supabase()

    def find_by_email(self, email: str) -> Optional[Usuario]:
        email = email.strip().lower()
        resp = (
            self._sb.table("profiles")
            .select(_COLUMNS)
            .ilike("email", email)
            .limit(1)
            .execute()
        )
        if not resp.data:
            return None
        return _row_a_usuario(resp.data[0])

    def find_by_id(self, user_id: str, gimnasio_id: Optional[str] = None) -> Optional[Usuario]:
        query = (
            self._sb.table("profiles")
            .select(_COLUMNS)
            .eq("id", user_id)
        )
        if gimnasio_id is not None:
            query = query.eq("gimnasio_id", gimnasio_id)
        resp = query.limit(1).execute()
        if not resp.data:
            return None
        return _row_a_usuario(resp.data[0])

    def listar_todos(self) -> List[Usuario]:
        resp = (
            self._sb.table("profiles")
            .select(_COLUMNS)
            .order("nombre")
            .execute()
        )
        return [_row_a_usuario(row) for row in (resp.data or [])]

    def listar_por_gimnasio(self, gimnasio_id: str) -> List[Usuario]:
        resp = (
            self._sb.table("profiles")
            .select(_COLUMNS)
            .eq("gimnasio_id", gimnasio_id)
            .order("nombre")
            .execute()
        )
        return [_row_a_usuario(row) for row in (resp.data or [])]

    def actualizar(
        self,
        user_id: str,
        nombre: Optional[str] = None,
        altura: Optional[float] = None,
        peso_actual: Optional[float] = None,
        peso_objetivo: Optional[float] = None,
        imagen_url: Optional[str] = None,
        porcentaje_grasa: Optional[float] = None,
        fecha_medicion_grasa: Optional[str] = None,
        origen_grasa: Optional[str] = None,
        cargado_por_id: Optional[str] = None,
        bio: Optional[str] = None,
        especialidades: Optional[List[str]] = None,
        anios_experiencia: Optional[int] = None,
        telefono: Optional[str] = None,
        notas_profesor: Optional[str] = None,
    ) -> Optional[Usuario]:
        update_data: dict = {}
        if nombre is not None: update_data["nombre"] = nombre
        if altura is not None: update_data["altura"] = altura
        if peso_actual is not None: update_data["peso_actual"] = peso_actual
        if peso_objetivo is not None: update_data["peso_objetivo"] = peso_objetivo
        if imagen_url is not None: update_data["imagen_url"] = imagen_url
        if porcentaje_grasa is not None: update_data["porcentaje_grasa"] = porcentaje_grasa
        if fecha_medicion_grasa is not None: update_data["fecha_medicion_grasa"] = fecha_medicion_grasa
        if origen_grasa is not None: update_data["origen_grasa"] = origen_grasa
        if cargado_por_id is not None: update_data["cargado_por_id"] = cargado_por_id
        if bio is not None: update_data["bio"] = bio
        if especialidades is not None: update_data["especialidades"] = especialidades
        if anios_experiencia is not None: update_data["anios_experiencia"] = anios_experiencia
        if telefono is not None: update_data["telefono"] = telefono
        if notas_profesor is not None: update_data["notas_profesor"] = notas_profesor

        if not update_data:
            return self.find_by_id(user_id)

        resp = (
            self._sb.table("profiles")
            .update(update_data)
            .eq("id", user_id)
            .execute()
        )
        if not resp.data:
            return None
        return _row_a_usuario(resp.data[0])