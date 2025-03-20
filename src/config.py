from configparser import ConfigParser


COMPANY_NAMES = [
    "МедРокет",
    "MIP",
    "АО Кубаньторгбанк",
    "Мореон инвест",
    "Бронируй Онлайн",
    "AdminMobile",
    "VIDEO INSIDE",
    "WILIX",
    "HRКАДРЫ",
    "YAKHA"
]


def config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename, encoding='UTF-8')
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} is not found  in the {1} file'.format(section, filename))
    return db

