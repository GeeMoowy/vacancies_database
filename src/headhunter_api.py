from typing import Any, Dict, List

import requests

from src.base_api import BaseAPI
from src.config import COMPANY_NAMES


class HeadHunterAPI(BaseAPI):
    """Класс подключается к API hh.ru и получает вакансии"""

    base_url: str
    headers: dict

    def __init__(self) -> None:
        """Конструктор метода для организации запроса на API hh.ru"""

        self.__base_url = 'https://api.hh.ru/vacancies'
        self.__headers = {'User-Agent': 'HH-User-Agent'}

    def __connect(self) -> requests.Response:
        """Метод для проверки подключения к API hh.ru"""

        response = requests.get(self.__base_url, headers=self.__headers)
        if response.status_code != 200:
            raise Exception(f"Ошибка подключения {response.status_code}")
        return response

    def get_vacancies(self) -> List[Dict[str, Any]]:
        """Метод получает вакансии сайта hh.ru по ключевому слову"""

        vacancies = []

        for company_name in COMPANY_NAMES:  # Используем список компаний из config.py
            # Ищем компании по названию
            employer_response = requests.get(
                'https://api.hh.ru/employers',
                headers=self.__headers,
                params={'text': company_name}
            )

            if employer_response.status_code != 200:
                raise Exception(f"Ошибка получения данных о компании {company_name}: {employer_response.status_code}")

            employers = employer_response.json().get('items', [])

            if not employers:
                print(f"Компания '{company_name}' не найдена.")
                continue

            # Берем первый результат (самый релевантный)
            employer_id = employers[0]['id']

            # Получаем вакансии для компании
            params = {'employer_id': employer_id, 'per_page': 100}
            response = requests.get(self.__base_url, headers=self.__headers, params=params)

            if response.status_code != 200:
                raise Exception(f"Ошибка получения вакансий для компании {company_name}: {response.status_code}")

            company_vacancies = response.json().get('items', [])
            vacancies.extend(company_vacancies)

        return vacancies
