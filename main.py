from src.db_manager import DBManager
from src.headhunter_api import HeadHunterAPI


def main() -> None:
    """Функция для взаимодействия с пользователем"""

    vacancy = HeadHunterAPI()
    vacancies_hh = vacancy.get_vacancies()
    vacancies_database = DBManager('tests')
    vacancies_database.create_database()
    vacancies_database.fill_vacancies(vacancies_hh)
    print("Добро пожаловать в базу данных вакансий сайта hh.ru")
    while True:
        user_selection = input("Выберите следующее действие:\n"
                               "1 - Показать название компаний и количество вакансий\n"
                               "2 - Посмотреть все вакансии\n"
                               "3 - Получить среднюю зарплату по всем вакансиям\n"
                               "4 - Посмотреть вакансии с зарплатами выше средней\n"
                               "5 - Получить вакансии по ключевому слову в названии\n"
                               "6 - Выход\n"
                               "Выберите цифру от 1 до 6: ")

        if user_selection == '1':
            result = vacancies_database.get_companies_and_vacancies_count()
            for company_name, vacancies_count in result:
                print(f"Компания: {company_name}, Количество вакансий: {vacancies_count}")
        elif user_selection == '2':
            result = vacancies_database.get_all_vacancies()
            for company_name, vacancy_name, salary, vacancy_url in result:
                print(f"Компания: {company_name}, Вакансия: {vacancy_name}, Зарплата: {salary}, Ссылка: {vacancy_url}")
        elif user_selection == '3':
            result = vacancies_database.get_avg_salary()
            print(result)
        elif user_selection == '4':
            result = vacancies_database.get_vacancies_with_higher_salary()
            for company_name, vacancy_name, salary, vacancy_url in result:
                print(f"Компания: {company_name}, Вакансия: {vacancy_name}, Зарплата: {salary}, Ссылка: {vacancy_url}")
        elif user_selection == '5':
            user_keywords = input('Введите ключевые слова для поиска через запятую: ').split()
            result = vacancies_database.get_vacancies_with_keyword(user_keywords)
            for company_name, vacancy_name, salary, vacancy_url in result:
                print(f"Компания: {company_name}, Вакансия: {vacancy_name}, Зарплата: {salary}, Ссылка: {vacancy_url}")
        elif user_selection == '6':
            break
        else:
            print('Некорректный ввод! Введите цифры от 1 и до 6')


if __name__ == "__main__":
    main()
