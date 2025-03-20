from src.db_manager import DBManager
from src.headhunter_api import HeadHunterAPI


if __name__ == "__main__":
    vacancy = HeadHunterAPI()
    vacancies_hh = vacancy.get_vacancies()
    res = DBManager('tests')
    res.create_database()
    res.fill_vacancies(vacancies_hh)
    # result = res.get_companies_and_vacancies_count()
    # for company_name, vacancies_count in result:
    #     print(f"Компания: {company_name}, Количество вакансий: {vacancies_count}")
    result = res.get_all_vacancies()
    for company_name, vacancy_name, salary, vacancy_url in result:
        print(f"Компания: {company_name}, Вакансия: {vacancy_name}, Зарплата: {salary}, Ссылка: {vacancy_url}")
