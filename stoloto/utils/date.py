import datetime


class DateFormat:
    DMY_DOTTED = '%d.%m.%Y'
    YMD_DOTTED = '%Y.%m.%d'
    DMY_SPACED = '%d %m %Y'

    def __iter__(self):
        for attr_name, value in self.__class__.__dict__.items():
            if attr_name.startswith('__'):
                continue
            if isinstance(value, (int, str, bool, list, tuple, dict,)):
                yield value


def guess_format(date_str, date_format_str=''):
    if issubclass(type(date_str), datetime.datetime):
        return date_str

    if date_format_str:
        try:
            return datetime.datetime.strptime(date_str, date_format_str)
        except ValueError:
            pass

    for date_format_str in DateFormat():
        try:
            return datetime.datetime.strptime(date_str, date_format_str)
        except ValueError:
            continue
    raise ValueError(f'Can\'t guess format for {date_str}')


def today(days_ago: int = 0, date_format: str = DateFormat.DMY_DOTTED) -> str:
    date_ = datetime.date.today() if 0 > days_ago else datetime.date.today() - datetime.timedelta(days=days_ago)
    return date_.strftime(date_format)


def delta_days(from_date, to_date=None, date_format_str: str = DateFormat.DMY_SPACED) -> int:
    if to_date is None or to_date == '':
        to_date_ = datetime.datetime.now()
    else:
        to_date_ = guess_format(to_date, date_format_str)

    from_date_ = guess_format(from_date, date_format_str)
    delta = to_date_ - from_date_
    return delta.days


def filter_by(date_strings_iterable, condition_func):
    if condition_func and callable(condition_func):
        for date_str in date_strings_iterable:
            dt = guess_format(date_str)
            if bool(condition_func(dt)):
                yield date_str
