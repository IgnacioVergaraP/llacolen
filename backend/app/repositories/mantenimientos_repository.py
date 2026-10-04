"""
Interfaz del repositorio de mantenciones.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models import Mantenimiento


class MantenimientosRepository(ABC):

    @abstractmethod
    def crear(self, mantenimiento: Mantenimiento) -> Mantenimiento:
        ...

    @abstractmethod
    def find_by_id(self, mantenimiento_id: str) -> Optional[Mantenimiento]:
        ...

    @abstractmethod
    def listar_por_maquina(self, maquina_id: str, gimnasio_id: str) -> List[Mantenimiento]:
        ...

    @abstractmethod
    def listar_todos(self, gimnasio_id: str) -> List[Mantenimiento]:
        ...

    @abstractmethod
    def ultima_por_maquina(self, maquina_id: str) -> Optional[Mantenimiento]:
        ...

    @abstractmethod
    def eliminar(self, mantenimiento_id: str) -> bool:
        ...