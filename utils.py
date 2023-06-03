import settings
from telebot import types

def generate_markup(buttons):
    """
    Создаем клавиатуру с кнопками

    :param buttons: Массив кнопок
    :return: Объект клавиатуры
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for row in buttons:
        markup.add(*[telebot.types.InlineKeyboardButton(text=name) for name in row])

    return markup

def get_markup():
    """
    Выводит объект клавиатуры

    :return: Объект клавиатуры
    """
    return generate_markup([[settings.CMD_DATETIME, settings.CMD_WEATHER], [settings.CMD_RATES, settings.CMD_HELP]])

def deg_to_compass(num):
    """
    Конвертирует направление ветра из градусов в розу

    :param num: Градус
    :return: Направление ветра по розе
    """
    val = int((num / 22.5) + .5)
    #arr = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    arr = ["С", "ССВ", "СВ", "ВСВ", "В", "ВЮВ", "ЮВ", "ЮЮВ", "Ю", "ЮЮЗ", "ЮЗ", "ЗЮЗ", "З", "ЗСЗ", "СЗ", "ССЗ"]
    return arr[(val % 16)]

def get_weather(city_abbr = "prm"):
    """
    Выводит погоду для Города
    :return: Сообщение о погоде в Городе на текущий день
    """
    url = "http://api.openweathermap.org/data/2.5/weather"
    if(city_abbr == "prm"):
        city_id = settings.prm_city_id
        city_name_where = "В Перми"
    if(city_abbr == "yvn"):
        city_id = settings.yvn_city_id
        city_name_where = "В Ереване"
    response = requests.session().get('%s?id=%s&units=metric&appid=%s' % (url, city_id, os.getenv('OPENWEATHERMAP_TOKEN'))).json()

    if(response['cod'] == 200):
        t = str(response['main']['temp'])
        wind_deg = response['wind']['deg']
        wind_speed = str(response['wind']['speed'])
        text = '\U0001f326 %s %s °C\n\U0001f32c %s %sм/с\n' % (city_name_where, t, deg_to_compass(wind_deg), wind_speed)

        return text
    else:
        return False