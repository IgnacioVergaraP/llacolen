"""
Interfaz del repositorio de máquinas.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models import Maquina


class MaquinasRepository(ABC):

    @abstractmethod
    def listar(self, gimnasio_id: str) -> List[Maquina]:
        ...

    @abstractmethod
    def listar_por_musculo(self, musculo: str, gimnasio_id: str) -> List[Maquina]:
        ...

    @abstractmethod
    def find_by_id(self, maquina_id: str, gimnasio_id: Optional[str] = None) -> Optional[Maquina]:
        ...

    @abstractmethod
    def crear(
        self,
        nombre: str,
        grupos_musculares: List[str],
        descripcion: str,
        video_url: str,
        gimnasio_id: str,
        imagen_url: str = "",
    ) -> Maquina:
        ...