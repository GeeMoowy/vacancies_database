from src.base_db_manager import BaseDBManager
import psycopg2

from src.config import config, COMPANY_NAMES


class DBManager(BaseDBManager):
    """Класс, который подключается к БД PostgreSQL и работает с ней"""

    def __init__(self, db_name: str):
        self.db_name = db_name
        self.params = config()

    def create_database(self):
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

    def fill_companies(self):
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

    def fill_vacancies(self, vacancies_data: list[dict]):
        """
        Заполняет таблицу vacancies данными из списка словарей.
        :param vacancies_data: Список словарей с данными о вакансиях.
        """
        conn = psycopg2.connect(dbname=self.db_name, **self.params)
        with conn.cursor() as cur:
            for vacancy in vacancies_data:
                # Получаем данные из словаря
                vacancy_id = vacancy.get('id')
                print(vacancy_id)
                vacancy_name = vacancy.get('name')
                print(vacancy_name)
                salary = vacancy.get('salary', {})  # Получаем словарь с зарплатой
                salary_from = salary.get('from') if salary else None  # Зарплата "от"
                print(salary_from)
                vacancy_url = vacancy.get('url')
                print(vacancy_url)

                # Если зарплата не указана, устанавливаем значение по умолчанию
                if salary_from is None:
                    salary_from = 0
                    print(salary_from)

                # Получаем company_id по названию компании (если есть)
                company_name = vacancy.get('employer', {}).get('name')  # Название компании
                print(company_name)
                if company_name:
                    cur.execute("""
                        SELECT company_id FROM companies WHERE company_name = %s
                    """, (company_name,))
                    company_id = cur.fetchone()
                    if company_id:
                        company_id = company_id[0]
                    else:
                        # Если компании нет в таблице, пропускаем вакансию
                        continue
                else:
                    # Если название компании отсутствует, пропускаем вакансию
                    continue

                # Вставляем данные в таблицу vacancies
                cur.execute("""
                    INSERT INTO vacancies (vacancy_id, company_id, vacancy_name, salary, vacancy_url)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (vacancy_id) DO NOTHING
                """, (vacancy_id, company_id, vacancy_name, salary_from, vacancy_url))

        conn.commit()
        conn.close()


    def get_companies_and_vacancies_count(self, *args, **kwargs):
        """Метод получает список всех компаний и количество вакансий у каждой компании"""
        pass

    def get_all_vacancies(self, *args, **kwargs):
        """Метод получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию"""
        pass

    def get_avg_salary(self, *args, **kwargs):
        """Метод получает среднюю зарплату по вакансиям"""
        pass

    def get_vacancies_with_higher_salary(self, *args, **kwargs):
        """Метод получает список всех вакансий, у которых зарплата выше средней по всем вакансиям"""
        pass

    def get_vacancies_with_keyword(self, *args, **kwargs):
        """Метод получает список всех вакансий,
        в названии которых содержатся переданные в метод слова, например python."""
        pass
