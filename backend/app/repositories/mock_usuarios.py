"""
Mock de usuarios para TESTS UNITARIOS.

Este repositorio ya NO se usa en producción (el runtime usa
SupabaseUsuariosRepository). Se mantiene acá porque los tests
unitarios necesitan una fuente de usuarios en memoria que no
dependa de red.

La fixture `mock_auth` de tests/conftest.py lo inyecta en el
módulo de decoradores para simular la autenticación.
"""
from copy import deepcopy
from typing import Optional, List
from app.domain.models import Usuario
from app.repositories.usuarios_repository import UsuariosRepository


_USUARIOS_MOCK: List[Usuario] = [
    Usuario(
        id="u-gim-001",
        email="admin@gimnasio.com",
        nombre="Admin Gimnasio",
        rol="gimnasio",
        gimnasio_id="mock-gym",
        fecha_alta="2024-01-15",
    ),
    Usuario(
        id="u-pro-001",
        email="profesor@gimnasio.com",
        nombre="Prof. Martínez",
        rol="profesor",
        gimnasio_id="mock-gym",
        bio="Especialista en hipertrofia y fuerza. 8 años acompañando alumnos en su progreso.",
        especialidades=["musculación", "fuerza", "hipertrofia"],
        anios_experiencia=8,
        telefono="+54 11 5555-1234",
        fecha_alta="2024-03-08",
    ),
    Usuario(
        id="u-alu-001",
        email="alumno@gimnasio.com",
        nombre="Juan Pérez",
        rol="alumno",
        gimnasio_id="mock-gym",
        altura=178.0,
        peso_actual=74.5,
        peso_objetivo=70.0,
        porcentaje_grasa=14.5,
        fecha_medicion_grasa="2026-09-15",
        origen_grasa="profesor",
        cargado_por_id="u-pro-001",
        notas_profesor="Buena técnica en press de banca. Trabajar movilidad de hombro derecho.",
        fecha_alta="2025-06-20",
    ),
    Usuario(
        id="u-alu-002",
        email="maria.gonzalez@gimnasio.com",
        nombre="María González",
        rol="alumno",
        gimnasio_id="mock-gym",
        altura=165.0,
        peso_actual=58.0,
        peso_objetivo=60.0,
        porcentaje_grasa=22.0,
        fecha_medicion_grasa="2026-09-10",
        origen_grasa="profesor",
        cargado_por_id="u-pro-001",
        fecha_alta="2025-09-12",
    ),
    Usuario(
        id="u-alu-003",
        email="carlos.rodriguez@gimnasio.com",
        nombre="Carlos Rodríguez",
        rol="alumno",
        gimnasio_id="mock-gym",
        altura=182.0,
        peso_actual=88.0,
        peso_objetivo=80.0,
        porcentaje_grasa=18.5,
        fecha_medicion_grasa="2026-09-20",
        origen_grasa="profesor",
        cargado_por_id="u-pro-001",
        fecha_alta="2025-11-03",
    ),
    Usuario(
        id="u-alu-004",
        email="lucia.fernandez@gimnasio.com",
        nombre="Lucía Fernández",
        rol="alumno",
        gimnasio_id="mock-gym",
        altura=170.0,
        peso_actual=62.0,
        imagen_url=None,
        fecha_alta="2026-01-08",
    ),
]


class MockUsuariosRepository(UsuariosRepository):

    def __init__(self):
        self._usuarios: List[Usuario] = deepcopy(_USUARIOS_MOCK)

    def find_by_email(self, email: str) -> Optional[Usuario]:
        email = email.strip().lower()
        for u in self._usuarios:
            if u.email.lower() == email:
                return u
        return None

    def find_by_id(self, user_id: str, gimnasio_id: Optional[str] = None) -> Optional[Usuario]:
        for u in self._usuarios:
            if u.id == user_id and (gimnasio_id is None or u.gimnasio_id == gimnasio_id):
                return u
        return None

    def listar_todos(self) -> List[Usuario]:
        return list(self._usuarios)

    def listar_por_gimnasio(self, gimnasio_id: str) -> List[Usuario]:
        return [u for u in self._usuarios if u.gimnasio_id == gimnasio_id]

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
        usuario = self.find_by_id(user_id)
        if not usuario:
            return None
        if nombre is not None: usuario.nombre = nombre
        if altura is not None: usuario.altura = altura
        if peso_actual is not None: usuario.peso_actual = peso_actual
        if peso_objetivo is not None: usuario.peso_objetivo = peso_objetivo
        if imagen_url is not None: usuario.imagen_url = imagen_url
        if porcentaje_grasa is not None: usuario.porcentaje_grasa = porcentaje_grasa
        if fecha_medicion_grasa is not None: usuario.fecha_medicion_grasa = fecha_medicion_grasa
        if origen_grasa is not None: usuario.origen_grasa = origen_grasa
        if cargado_por_id is not None: usuario.cargado_por_id = cargado_por_id
        if bio is not None: usuario.bio = bio
        if especialidades is not None: usuario.especialidades = list(especialidades)
        if anios_experiencia is not None: usuario.anios_experiencia = anios_experiencia
        if telefono is not None: usuario.telefono = telefono
        if notas_profesor is not None: usuario.notas_profesor = notas_profesor
        return usuario