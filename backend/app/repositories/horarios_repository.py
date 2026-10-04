"""
Interfaz del repositorio de horarios.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models import Horario


class HorariosRepository(ABC):

    @abstractmethod
    def listar(self, gimnasio_id: str, profesor_id: Optional[str] = None) -> List[Horario]:
        ...

    @abstractmethod
    def find_by_id(self, horario_id: str) -> Optional[Horario]:
        ...

    @abstractmethod
    def crear(self, horario: Horario) -> Horario:
        ...

    @abstractmethod
    def actualizar(self, horario_id: str, data: dict) -> Optional[Horario]:
        ...

    @abstractmethod
    def eliminar(self, horario_id: str) -> bool:
        ...

    @abstractmethod
    def hay_solapamiento(
        self,
        profesor_id: str,
        dia_semana: int,
        hora_inicio: str,
        hora_fin: str,
        excluir_id: Optional[str] = None,
    ) -> bool:
        ...