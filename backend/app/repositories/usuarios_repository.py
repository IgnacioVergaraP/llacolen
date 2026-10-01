"""
Interfaz del repositorio de usuarios.

Contrato que debe cumplir cualquier implementación concreta
(actualmente Supabase; antes MockUsuariosRepository).
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models import Usuario


class UsuariosRepository(ABC):

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[Usuario]:
        ...

    @abstractmethod
    def find_by_id(self, user_id: str) -> Optional[Usuario]:
        ...

    @abstractmethod
    def listar_todos(self) -> List[Usuario]:
        ...

    @abstractmethod
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
        ...