from typing import Any, Dict, List, Tuple

import psycopg2

from src.base_db_manager import BaseDBManager
from src.config import COMPANY_NAMES, config


class DBManager(BaseDBManager):
    """Класс, который подключается к БД PostgreSQL и работает с ней"""

    def __init__(self, db_name: str) -> None:
        self.db_name = db_name
        self.params = config()

    def create_database(self) -> None:
        """Создание базы данных и таблиц для работы с компаниями и вакансиями"""
        conn = psycopg2.connect(dbname='postgres', **self.params)
        conn.autocommit = True
        cur = conn.cursor()

        cur.execute(f"DROP DATABASE IF EXISTS {self.db_name}")
        cur.execute(f"CREATE DATABASE {self.db_name}")

        cur.close()
        conn.close()

        conn = psycopg2.connect(dbname=self.db_name, **self.params)
        with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE companies (
                company_id SERIAL PRIMARY KEY,
                company_name VARCHAR(255) UNIQUE
            )
            """)

        with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE vacancies (
                vacancy_id INT PRIMARY KEY,
                company_id INT REFERENCES companies(company_id),
                vacancy_name VARCHAR(255),
                salary FLOAT,
                vacancy_url TEXT
            )
            """)

        conn.commit()
        conn.close()

        self.fill_companies()

    def fill_companies(self) -> None:
        """Заполняет таблицу companies данными из списка в модуле config.py"""
        conn = psycopg2.connect(dbname=self.db_name, **self.params)
        with conn.cursor() as cur:
            for company_name in COMPANY_NAMES:
                cur.execute("""
                    INSERT INTO companies (company_name)
                    VALUES (%s)
                    ON CONFLICT (company_name) DO NOTHING
                """, (company_name,))

        conn.commit()
        conn.close()

    def fill_vacancies(self, vacancies_data: List[Dict[str, Any]]) -> None:
        """Заполняет таблицу vacancies данными из списка словарей"""
        conn = psycopg2.connect(dbname=self.db_name, **self.params)
        with conn.cursor() as cur:
            for vacancy in vacancies_data:

                vacancy_id = vacancy.get('id')  # Получаем данные из словаря
                vacancy_name = vacancy.get('name')
                salary = vacancy.get('salary', {})  # Получаем словарь с зарплатой
                salary_from = salary.get('from') if salary else None  # Зарплата "от"
                vacancy_url = vacancy.get('url')

                if salary_from is None:  # Если зарплата не указана, устанавливаем значение по умолчанию
                    salary_from = 0

                company_name = vacancy.get('employer', {}).get('name')  # Название компании
                if company_name:
                    cur.execute("""
                        SELECT company_id FROM companies WHERE company_name = %s
                    """, (company_name,))
                    company_id = cur.fetchone()
                    if company_id:
                        company_id = company_id[0]
                    else:
                        continue  # Если компании нет в таблице, пропускаем вакансию
                else:
                    continue  # Если название компании отсутствует, пропускаем вакансию

                cur.execute("""
                    INSERT INTO vacancies (vacancy_id, company_id, vacancy_name, salary, vacancy_url)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (vacancy_id) DO NOTHING
                """, (vacancy_id, company_id, vacancy_name, salary_from, vacancy_url))

        conn.commit()
        conn.close()

    def get_companies_and_vacancies_count(self) -> List[Tuple]:
        """Возвращает список всех компаний и количество вакансий у каждой компании"""
        conn = psycopg2.connect(dbname=self.db_name, **self.params)
        with conn.cursor() as cur:
            cur.execute("""
                SELECT companies.company_name, COUNT(vacancies.vacancy_id) AS vacancies_count
                FROM companies
                LEFT JOIN vacancies ON companies.company_id = vacancies.company_id
                GROUP BY companies.company_name
                ORDER BY vacancies_count DESC
            """)
            result = cur.fetchall()  # Получаем результат запроса

        conn.close()
        return result

    def get_all_vacancies(self) -> List[Tuple]:
        """Метод получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию"""
        conn = psycopg2.connect(dbname=self.db_name, **self.params)
        with conn.cursor() as cur:
            # SQL-запрос для получения всех вакансий
            cur.execute("""
                    SELECT companies.company_name, vacancies.vacancy_name, vacancies.salary, vacancies.vacancy_url
                    FROM vacancies
                    INNER JOIN companies ON vacancies.company_id = companies.company_id
                """)
            result = cur.fetchall()  # Получаем результат запроса

        conn.close()
        return result

    def get_avg_salary(self) -> float:
        """Метод получает среднюю зарплату по вакансиям"""
        conn = psycopg2.connect(dbname=self.db_name, **self.params)
        with conn.cursor() as cur:
            # SQL-запрос для получения средней зарплаты
            cur.execute("""
                    SELECT AVG(salary) FROM vacancies
                """)
            avg_salary = cur.fetchone()[0]  # Получаем результат запроса

        conn.close()
        return f"Средняя зарплата по всем вакансиям в базе данных = {avg_salary}" if avg_salary is not None else 0

    def get_vacancies_with_higher_salary(self) -> List[Tuple]:
        """Метод получает список всех вакансий, у которых зарплата выше средней по всем вакансиям"""
        conn = psycopg2.connect(dbname=self.db_name, **self.params)
        with conn.cursor() as cur:
            # Получаем среднюю зарплату
            cur.execute("SELECT AVG(salary) FROM vacancies WHERE salary IS NOT NULL")
            avg_salary = cur.fetchone()[0]

            # Получаем вакансии с зарплатой выше средней
            cur.execute("""
                    SELECT companies.company_name, vacancies.vacancy_name, vacancies.salary, vacancies.vacancy_url
                    FROM vacancies
                    INNER JOIN companies ON vacancies.company_id = companies.company_id
                    WHERE vacancies.salary > %s
                """, (avg_salary,))

            result = cur.fetchall()  # Получаем результат запроса

        conn.close()
        return result

    def get_vacancies_with_keyword(self, keywords: List[str]) -> List[Tuple]:
        """Метод получает список всех вакансий,
        в названии которых содержатся переданные в метод слова, например python."""
        conn = psycopg2.connect(dbname=self.db_name, **self.params)
        with conn.cursor() as cur:
            # Создаем условия для запроса
            conditions = []
            params = []

            for keyword in keywords:
                conditions.append("vacancies.vacancy_name ILIKE %s")
                params.append(f'%{keyword}%')

            # Соединяем условия через OR
            query = f"""
                SELECT companies.company_name, vacancies.vacancy_name, vacancies.salary, vacancies.vacancy_url
                FROM vacancies
                INNER JOIN companies ON vacancies.company_id = companies.company_id
                WHERE {' OR '.join(conditions)}
            """

            cur.execute(query, params)  # Передаем параметры запроса
            result = cur.fetchall()  # Получаем результат запроса

        conn.close()
        return result
