"""Lógica de negocio del módulo rutinas (vista alumno)."""
from typing import List
from app.errors import AuthError
from app.repositories.mock_rutinas import MockRutinasRepository
from app.repositories.mock_maquinas import MockMaquinasRepository


_rutinas_repo = MockRutinasRepository()
_maquinas_repo = MockMaquinasRepository()


def listar_rutinas(alumno_id: str, incluir_inactivas: bool = False) -> List[dict]:
    rutinas = _rutinas_repo.listar_por_alumno(alumno_id, incluir_inactivas=incluir_inactivas)
    return [r.to_dict() for r in rutinas]


def obtener_rutina(rutina_id: str, alumno_id: str) -> dict:
    rutina = _rutinas_repo.find_by_id(rutina_id)
    if not rutina or rutina.alumno_id != alumno_id:
        raise AuthError(
            404, "NotFound",
            f"No existe una rutina con id '{rutina_id}' para este usuario.",
        )

    maquinas_por_id = {}
    for ej in rutina.ejercicios:
        if ej.tipo == "maquina" and ej.maquina_id:
            m = _maquinas_repo.find_by_id(ej.maquina_id)
            if m:
                maquinas_por_id[m.id] = m

    return rutina.to_dict_resuelto(maquinas_por_id)


# -------- Helpers reusables por el blueprint profesor --------

def listar_rutinas_por_alumno_id(alumno_id: str, incluir_inactivas: bool = False) -> List[dict]:
    return listar_rutinas(alumno_id, incluir_inactivas=incluir_inactivas)


def obtener_rutina_resuelta(rutina_id: str) -> dict | None:
    """
    Devuelve la rutina resuelta con datos de máquinas, sin chequear pertenencia.
    Usado desde el panel del profesor. Devuelve None si no existe.
    """
    rutina = _rutinas_repo.find_by_id(rutina_id)
    if not rutina:
        return None

    maquinas_por_id = {}
    for ej in rutina.ejercicios:
        if ej.tipo == "maquina" and ej.maquina_id:
            m = _maquinas_repo.find_by_id(ej.maquina_id)
            if m:
                maquinas_por_id[m.id] = m

    return rutina.to_dict_resuelto(maquinas_por_id)