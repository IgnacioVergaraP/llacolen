"""Lógica de negocio del módulo admin."""
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from collections import Counter

from app.errors import AuthError
from app.domain.models import Horario, Mantenimiento
from app.repositories.supabase_horarios import SupabaseHorariosRepository
from app.repositories.supabase_usuarios import SupabaseUsuariosRepository
from app.repositories.supabase_maquinas import SupabaseMaquinasRepository
from app.repositories.supabase_mantenimientos import SupabaseMantenimientosRepository   


_horarios_repo = SupabaseHorariosRepository()
_usuarios_repo = SupabaseUsuariosRepository()
_maquinas_repo = SupabaseMaquinasRepository()
_mantenimientos_repo = SupabaseMantenimientosRepository()


def _progreso_repo():
    """Import perezoso para evitar ciclos."""
    from app.repositories.supabase_progreso import SupabaseProgresoRepository
    return SupabaseProgresoRepository()


# -------- Profesores --------

def listar_profesores() -> List[dict]:
    todos = _usuarios_repo.listar_todos()
    profes = [u for u in todos if u.rol in ("profesor", "gimnasio") and u.activo]
    profes.sort(key=lambda u: u.nombre.lower())
    return [{"id": u.id, "nombre": u.nombre, "rol": u.rol} for u in profes]


# -------- Horarios --------

def listar_horarios(profesor_id: Optional[str] = None) -> List[dict]:
    horarios = _horarios_repo.listar(profesor_id)
    horarios.sort(key=lambda h: (h.dia_semana, h.hora_inicio))
    return [h.to_dict() for h in horarios]


def obtener_horario(horario_id: str) -> dict:
    h = _horarios_repo.find_by_id(horario_id)
    if not h:
        raise AuthError(404, "NotFound", f"No existe un horario con id '{horario_id}'.")
    return h.to_dict()


def crear_horario(payload: dict) -> dict:
    profesor = _usuarios_repo.find_by_id(payload["profesor_id"])
    if not profesor or profesor.rol not in ("profesor", "gimnasio"):
        raise AuthError(400, "InvalidProfesor", f"No existe un profesor con id '{payload['profesor_id']}'.")

    if _horarios_repo.hay_solapamiento(
        profesor_id=payload["profesor_id"],
        dia_semana=payload["dia_semana"],
        hora_inicio=payload["hora_inicio"],
        hora_fin=payload["hora_fin"],
    ):
        raise AuthError(400, "HorarioSolapado", "El profesor ya tiene un horario que se solapa con este.")

    horario = Horario(
        id="",
        profesor_id=profesor.id,
        profesor_nombre=profesor.nombre,
        dia_semana=payload["dia_semana"],
        hora_inicio=payload["hora_inicio"],
        hora_fin=payload["hora_fin"],
        notas=payload.get("notas"),
    )
    creado = _horarios_repo.crear(horario)
    return creado.to_dict()


def editar_horario(horario_id: str, payload: dict) -> dict:
    horario = _horarios_repo.find_by_id(horario_id)
    if not horario:
        raise AuthError(404, "NotFound", f"No existe un horario con id '{horario_id}'.")

    dia = payload.get("dia_semana", horario.dia_semana)
    h_inicio = payload.get("hora_inicio", horario.hora_inicio)
    h_fin = payload.get("hora_fin", horario.hora_fin)

    if h_inicio >= h_fin:
        raise AuthError(400, "InvalidRango", "'hora_inicio' debe ser menor que 'hora_fin'.")

    if _horarios_repo.hay_solapamiento(
        profesor_id=horario.profesor_id,
        dia_semana=dia,
        hora_inicio=h_inicio,
        hora_fin=h_fin,
        excluir_id=horario_id,
    ):
        raise AuthError(400, "HorarioSolapado", "El nuevo horario se solapa con otro del mismo profesor.")

    actualizado = _horarios_repo.actualizar(horario_id, payload)
    if not actualizado:
        raise AuthError(500, "UnexpectedError", "No se pudo actualizar.")
    return actualizado.to_dict()


def eliminar_horario(horario_id: str) -> dict:
    ok = _horarios_repo.eliminar(horario_id)
    if not ok:
        raise AuthError(404, "NotFound", f"No existe un horario con id '{horario_id}'.")
    return {"id": horario_id, "eliminado": True}


# -------- Dashboard de uso --------

_RANGOS_VALIDOS = {
    "7d": 7,
    "30d": 30,
    "90d": 90,
    "365d": 365,
}


def _dias_de_rango(rango: str) -> int:
    if rango not in _RANGOS_VALIDOS:
        raise AuthError(400, "InvalidRango", f"'rango' debe ser uno de: {', '.join(_RANGOS_VALIDOS.keys())}.")
    return _RANGOS_VALIDOS[rango]


def obtener_dashboard_uso(rango: str) -> dict:
    """
    Analítica de uso de máquinas basada en los registros de series de los alumnos.
    """
    dias = _dias_de_rango(rango)
    corte = datetime.now(timezone.utc) - timedelta(days=dias)

    repo = _progreso_repo()
    alumnos = _usuarios_repo.listar_todos()

    todos = []
    for u in alumnos:
        if u.rol != "alumno":
            continue
        todos.extend(repo.listar_por_alumno(u.id))

    # Filtro por fecha + solo tipo máquina
    contador = Counter()
    total_series = 0
    for r in todos:
        if r.ejercicio_tipo != "maquina" or not r.maquina_id:
            continue
        try:
            f = datetime.fromisoformat(r.fecha)
            # Normalizar a UTC para comparar manzanas con manzanas
            if f.tzinfo is None:
                f = f.replace(tzinfo=timezone.utc)
            if f < corte:
                continue
        except (ValueError, TypeError):
            continue
        contador[r.maquina_id] += 1
        total_series += 1

    # Enriquecer con el nombre de la máquina
    maquinas_todas = _maquinas_repo.listar()
    nombres = {m.id: m.nombre for m in maquinas_todas}

    ranking = []
    for maquina_id, cantidad in contador.items():
        ranking.append({
            "maquina_id": maquina_id,
            "maquina_nombre": nombres.get(maquina_id, maquina_id),
            "cantidad_series": cantidad,
        })
    ranking.sort(key=lambda x: x["cantidad_series"], reverse=True)

    # Máquinas con 0 uso (las que están en el catálogo pero no aparecen en ranking)
    sin_uso = []
    for m in maquinas_todas:
        if m.id not in contador:
            sin_uso.append({
                "maquina_id": m.id,
                "maquina_nombre": m.nombre,
                "cantidad_series": 0,
            })

    # "Menos usadas": las de menor cantidad del ranking + las que tienen 0 uso
    menos = ranking[-5:][::-1] if len(ranking) >= 5 else ranking[::-1]
    faltantes = max(0, 5 - len(menos))
    menos = menos + sin_uso[:faltantes]

    return {
        "rango": rango,
        "dias": dias,
        "total_series": total_series,
        "total_maquinas_usadas": len(contador),
        "top_usadas": ranking[:5],
        "menos_usadas": menos,
    }


# -------- Mantenciones --------

def _maquina_nombre(maquina_id: str) -> str:
    m = _maquinas_repo.find_by_id(maquina_id)
    return m.nombre if m else maquina_id


def listar_mantenimientos_maquina(maquina_id: str) -> dict:
    maquina = _maquinas_repo.find_by_id(maquina_id)
    if not maquina:
        raise AuthError(404, "NotFound", f"No existe una máquina con id '{maquina_id}'.")
    items = _mantenimientos_repo.listar_por_maquina(maquina_id)
    return {
        "maquina": maquina.to_dict(),
        "mantenimientos": [m.to_dict() for m in items],
    }


def listar_todos_mantenimientos() -> List[dict]:
    return [m.to_dict() for m in _mantenimientos_repo.listar_todos()]


def crear_mantenimiento(admin, payload: dict) -> dict:
    maquina = _maquinas_repo.find_by_id(payload["maquina_id"])
    if not maquina:
        raise AuthError(400, "InvalidMaquina", f"No existe una máquina con id '{payload['maquina_id']}'.")

    # Si viene fecha (YYYY-MM-DD), la convertimos a ISO con hora 12:00 UTC
    # para evitar problemas de zona horaria. Si no, usamos "ahora".
    if payload.get("fecha"):
        # "2026-10-01" → "2026-10-01T12:00:00+00:00"
        fecha_iso = f"{payload['fecha']}T12:00:00+00:00"
    else:
        fecha_iso = datetime.now(timezone.utc).isoformat()

    mantenimiento = Mantenimiento(
        id="",
        maquina_id=maquina.id,
        maquina_nombre=maquina.nombre,
        fecha=fecha_iso,
        tipo=payload["tipo"],
        notas=payload.get("notas"),
        realizado_por_id=admin.id,
        realizado_por_nombre=admin.nombre,
        origen="manual",
    )
    creado = _mantenimientos_repo.crear(mantenimiento)
    return creado.to_dict()


def eliminar_mantenimiento(mantenimiento_id: str) -> dict:
    ok = _mantenimientos_repo.eliminar(mantenimiento_id)
    if not ok:
        raise AuthError(404, "NotFound", f"No existe un mantenimiento con id '{mantenimiento_id}'.")
    return {"id": mantenimiento_id, "eliminado": True}


def registrar_mantenimiento_auto(reporte, admin) -> Optional[Mantenimiento]:
    """
    Se llama desde el blueprint profesor cuando se resuelve un reporte
    de tipo 'rota' o 'desgastada'.
    """
    if reporte.tipo not in ("rota", "desgastada"):
        return None
    if not reporte.maquina_id:
        return None

    mantenimiento = Mantenimiento(
        id="",
        maquina_id=reporte.maquina_id,
        maquina_nombre=reporte.maquina_nombre or reporte.maquina_id,
        fecha=datetime.now(timezone.utc).isoformat(),
        tipo="correctivo" if reporte.tipo == "rota" else "preventivo",
        notas=f"Auto-generado desde reporte: {reporte.descripcion[:200]}",
        realizado_por_id=admin.id,
        realizado_por_nombre=admin.nombre,
        origen="auto",
        reporte_id=reporte.id,
    )
    return _mantenimientos_repo.crear(mantenimiento)