"""
Interfaz del repositorio de gimnasios.
"""
from abc import ABC, abstractmethod
from typing import Optional
from app.domain.models import Gimnasio


class GimnasiosRepository(ABC):

    @abstractmethod
    def find_by_id(self, gimnasio_id: str) -> Optional[Gimnasio]:
        ...

    @abstractmethod
    def find_by_slug(self, slug: str) -> Optional[Gimnasio]:
        ...