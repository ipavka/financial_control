import datetime as dt
import pytz


def ru_date_unix():
    """ Принимает в "UTS" формате дату и делает название месяца на русском """
    month_list = ('Января', 'Февраля', 'Марта', 'Апреля', 'Мая', 'Июня',
                  'Июля', 'Августа', 'Сентября', 'Октября', 'Ноября', 'Декабря')
    tz = pytz.timezone("Europe/Moscow")
    time_str = dt.datetime.now(tz)
    month = (int(time_str.strftime('%m'))-1)
    date = time_str.strftime(f"%d_{month_list[month]}_%Y")
    time = time_str.strftime(f"%H:%M")
    return time, date


def make_date():
    """ Делает дату в формате 'datetime' """
    tz = pytz.timezone("Europe/Moscow")
    date = dt.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    return date


if __name__ == '__main__':
    pass
    print(make_date())
    # print(ru_date_unix()[0])
    print(ru_date_unix()[1])
    print(ru_date_unix())
