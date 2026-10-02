"""Lógica de negocio del módulo usuario."""
from datetime import datetime, timedelta, timezone, date
from typing import List, Optional

from app.domain.models import Usuario, RegistroSerie
from app.repositories.supabase_usuarios import SupabaseUsuariosRepository
from app.repositories.supabase_rutinas import SupabaseRutinasRepository
from app.repositories.supabase_progreso import SupabaseProgresoRepository


_usuarios_repo = SupabaseUsuariosRepository()
_rutinas_repo = SupabaseRutinasRepository()
_progreso_repo = SupabaseProgresoRepository()


def _calcular_imc(altura_cm, peso_kg) -> Optional[float]:
    if not altura_cm or not peso_kg:
        return None
    try:
        altura_m = float(altura_cm) / 100.0
        if altura_m <= 0:
            return None
        imc = float(peso_kg) / (altura_m ** 2)
        return round(imc, 1)
    except (ValueError, TypeError):
        return None


def _perfil_dict(usuario: Usuario, rol_solicitante: str) -> dict:
    """
    Construye el dict del perfil con IMC calculado.
    Filtra notas_profesor si el solicitante es alumno.
    """
    base = usuario.to_public_dict_for(rol_solicitante)
    base["imc"] = _calcular_imc(usuario.altura, usuario.peso_actual)
    return base


# -------- Lectura --------

def obtener_perfil(usuario: Usuario, rol_solicitante: Optional[str] = None) -> dict:
    """
    Perfil del usuario autenticado.
    Si rol_solicitante no se especifica, se usa usuario.rol.
    """
    rol = rol_solicitante or usuario.rol
    return _perfil_dict(usuario, rol)


def obtener_perfil_por_id(alumno_id: str, rol_solicitante: str) -> Optional[dict]:
    """
    Igual que obtener_perfil pero buscando por id.
    rol_solicitante determina si se incluyen notas_profesor.
    """
    usuario = _usuarios_repo.find_by_id(alumno_id)
    if not usuario:
        return None
    return _perfil_dict(usuario, rol_solicitante)


def _dias_con_registro(registros: List[RegistroSerie]) -> set:
    return {r.fecha[:10] for r in registros}


def _calcular_racha(dias: set, hoy: datetime) -> int:
    if not dias:
        return 0
    inicio = hoy.date()
    if inicio.isoformat() not in dias:
        inicio = inicio - timedelta(days=1)
    racha = 0
    cursor = inicio
    while cursor.isoformat() in dias:
        racha += 1
        cursor = cursor - timedelta(days=1)
    return racha


def _calcular_sesiones_mes(dias: set, hoy: datetime) -> int:
    prefijo_mes = hoy.strftime("%Y-%m")
    return sum(1 for d in dias if d.startswith(prefijo_mes))


def _calcular_resumen(alumno_id: str) -> dict:
    rutinas = _rutinas_repo.listar_por_alumno(alumno_id)
    registros = _progreso_repo.listar_por_alumno(alumno_id)

    hoy = datetime.now(timezone.utc)
    dias = _dias_con_registro(registros)

    return {
        "rutinas_activas": len(rutinas),
        "sesiones_mes": _calcular_sesiones_mes(dias, hoy),
        "racha_actual": _calcular_racha(dias, hoy),
    }


def obtener_resumen(usuario: Usuario) -> dict:
    return _calcular_resumen(usuario.id)


def obtener_resumen_por_id(alumno_id: str) -> dict:
    return _calcular_resumen(alumno_id)


# -------- Escritura --------

def actualizar_perfil(usuario: Usuario, payload: dict) -> dict:
    origen_grasa = None
    cargado_por_id = None
    fecha_medicion_grasa = payload.get("fecha_medicion_grasa")

    if payload.get("porcentaje_grasa") is not None:
        origen_grasa = "profesor" if usuario.rol in ("profesor", "gimnasio") else "alumno"
        cargado_por_id = usuario.id
        if not fecha_medicion_grasa:
            fecha_medicion_grasa = date.today().isoformat()

    actualizado = _usuarios_repo.actualizar(
        user_id=usuario.id,
        nombre=payload.get("nombre"),
        altura=payload.get("altura"),
        peso_actual=payload.get("peso_actual"),
        peso_objetivo=payload.get("peso_objetivo"),
        imagen_url=payload.get("imagen_url"),
        porcentaje_grasa=payload.get("porcentaje_grasa"),
        fecha_medicion_grasa=fecha_medicion_grasa,
        origen_grasa=origen_grasa,
        cargado_por_id=cargado_por_id,
        bio=payload.get("bio"),
        especialidades=payload.get("especialidades"),
        anios_experiencia=payload.get("anios_experiencia"),
        telefono=payload.get("telefono"),
    )
    if not actualizado:
        return usuario.to_public_dict_for(usuario.rol)
    # El propio usuario se está editando: usar su rol como solicitante
    return _perfil_dict(actualizado, actualizado.rol)