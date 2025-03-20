from abc import ABC, abstractmethod


class BaseAPI(ABC):
    """Базовый абстрактный класс для работы с API"""

    @abstractmethod
    def get_vacancies(self, *args, **kwargs):
        """Абстрактный метод, обязательный для реализации в дочерних классах"""
        pass
