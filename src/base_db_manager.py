from abc import ABC, abstractmethod


class BaseDBManager(ABC):
    """Абстрактный класс для класса работы с базой данных"""

    @abstractmethod
    def get_companies_and_vacancies_count(self, *args, **kwargs):
        """Метод получает список всех компаний и количество вакансий у каждой компании"""
        pass

    @abstractmethod
    def get_all_vacancies(self, *args, **kwargs):
        """Метод получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию"""
        pass

    @abstractmethod
    def get_avg_salary(self, *args, **kwargs):
        """Метод получает среднюю зарплату по вакансиям"""
        pass

    @abstractmethod
    def get_vacancies_with_higher_salary(self, *args, **kwargs):
        """Метод получает список всех вакансий, у которых зарплата выше средней по всем вакансиям"""
        pass

    @abstractmethod
    def get_vacancies_with_keyword(self, *args, **kwargs):
        """Метод получает список всех вакансий,
        в названии которых содержатся переданные в метод слова, например python."""
        pass
