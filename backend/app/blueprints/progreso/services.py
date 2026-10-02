"""Lógica de negocio del módulo progreso."""
from datetime import datetime, timezone
from typing import List, Dict
from collections import defaultdict

from app.errors import AuthError
from app.domain.models import RegistroSerie
from app.repositories.supabase_progreso import SupabaseProgresoRepository
from app.repositories.supabase_maquinas import SupabaseMaquinasRepository


_progreso_repo = SupabaseProgresoRepository()
_maquinas_repo = SupabaseMaquinasRepository()


def _key_de_registro(r: RegistroSerie) -> str:
    return r.maquina_id if r.ejercicio_tipo == "maquina" else (r.nombre_libre or "")


def _nombre_visible(r: RegistroSerie) -> str:
    if r.ejercicio_tipo == "maquina" and r.maquina_id:
        m = _maquinas_repo.find_by_id(r.maquina_id)
        return m.nombre if m else r.maquina_id
    return r.nombre_libre or "Ejercicio"


def _peso_numerico(peso_str: str) -> float | None:
    try:
        return float(peso_str.strip().lower().replace("kg", "").strip())
    except (ValueError, AttributeError):
        return None


def _peso_max_numerico(registros: List[RegistroSerie]) -> float:
    max_peso = 0.0
    for r in registros:
        n = _peso_numerico(r.peso)
        if n is not None and n > max_peso:
            max_peso = n
    return max_peso


def crear_serie(alumno_id: str, payload: dict) -> dict:
    fecha_iso = datetime.now(timezone.utc).isoformat()

    numero_serie = payload.get("numero_serie")
    if numero_serie is None:
        ejercicio_key = payload.get("maquina_id") or payload.get("nombre_libre") or ""
        fecha_dia = fecha_iso[:10]
        numero_serie = _progreso_repo.siguiente_numero_serie(alumno_id, ejercicio_key, fecha_dia)

    registro = RegistroSerie(
        id="",
        alumno_id=alumno_id,
        fecha=fecha_iso,
        ejercicio_tipo=payload["ejercicio_tipo"],
        numero_serie=numero_serie,
        peso=payload["peso"],
        repeticiones=payload["repeticiones"],
        maquina_id=payload.get("maquina_id"),
        nombre_libre=payload.get("nombre_libre"),
        rutina_id=payload.get("rutina_id"),
    )

    creado = _progreso_repo.crear(registro)
    return creado.to_dict()


def actualizar_serie(alumno_id: str, registro_id: str, payload: dict) -> dict:
    actualizado = _progreso_repo.actualizar(
        registro_id=registro_id,
        alumno_id=alumno_id,
        peso=payload["peso"],
        repeticiones=payload["repeticiones"],
    )
    if not actualizado:
        raise AuthError(404, "NotFound", f"No existe un registro con id '{registro_id}'.")
    return actualizado.to_dict()


def listar_historial(alumno_id: str) -> List[dict]:
    registros = _progreso_repo.listar_por_alumno(alumno_id)

    grupos: Dict[tuple, List[RegistroSerie]] = defaultdict(list)
    for r in registros:
        key = _key_de_registro(r)
        fecha_dia = r.fecha[:10]
        grupos[(key, fecha_dia)].append(r)

    filas = []
    for (key, fecha_dia), series in grupos.items():
        prim = series[0]
        peso_max = _peso_max_numerico(series)
        filas.append({
            "ejercicio": _nombre_visible(prim),
            "ejercicio_tipo": prim.ejercicio_tipo,
            "maquina_id": prim.maquina_id,
            "nombre_libre": prim.nombre_libre,
            "fecha": min(s.fecha for s in series),
            "cantidad_series": len(series),
            "peso_max": peso_max if peso_max > 0 else None,
            "rutina_id": prim.rutina_id,
        })

    filas.sort(key=lambda f: f["fecha"], reverse=True)
    return filas


def obtener_evolucion(alumno_id: str, ejercicio_key: str) -> dict:
    registros = _progreso_repo.listar_por_ejercicio(alumno_id, ejercicio_key)
    if not registros:
        return {
            "ejercicio": ejercicio_key,
            "ejercicio_tipo": None,
            "maquina_id": None,
            "nombre_libre": None,
            "puntos": [],
            "pr_historico": None,
        }

    prim = registros[0]
    nombre = _nombre_visible(prim)

    por_dia: Dict[str, List[RegistroSerie]] = defaultdict(list)
    for r in registros:
        por_dia[r.fecha[:10]].append(r)

    puntos = []
    for dia in sorted(por_dia.keys()):
        series = por_dia[dia]
        peso_max = _peso_max_numerico(series)
        if peso_max <= 0:
            continue
        puntos.append({
            "fecha": dia,
            "peso_max": peso_max,
            "cantidad_series": len(series),
        })

    pr_historico = _peso_max_numerico(registros)

    return {
        "ejercicio": nombre,
        "ejercicio_tipo": prim.ejercicio_tipo,
        "maquina_id": prim.maquina_id,
        "nombre_libre": prim.nombre_libre,
        "puntos": puntos,
        "pr_historico": pr_historico if pr_historico > 0 else None,
    }


def obtener_sesion(alumno_id: str, ejercicio_key: str, fecha_dia: str) -> dict:
    series = _progreso_repo.listar_sesion(alumno_id, ejercicio_key, fecha_dia)
    if not series:
        raise AuthError(
            404,
            "NotFound",
            "No existe una sesión con esos datos para este usuario.",
        )

    prim = series[0]
    nombre = _nombre_visible(prim)

    return {
        "ejercicio": nombre,
        "ejercicio_tipo": prim.ejercicio_tipo,
        "maquina_id": prim.maquina_id,
        "nombre_libre": prim.nombre_libre,
        "fecha": fecha_dia,
        "series": [
            {
                "id": s.id,
                "numero_serie": s.numero_serie,
                "peso": s.peso,
                "repeticiones": s.repeticiones,
            }
            for s in series
        ],
    }