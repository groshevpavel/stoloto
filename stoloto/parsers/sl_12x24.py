from stoloto.parsers import MAPPING_LOTTERY_HTML
from stoloto.parsers.sl_lottery_parser import DefaultLotteryParser
from stoloto.utils.date import delta_days

MAPPING_FOR_DICT = [
    'draw_date',
    'draw_num',
    'draw_stats_link',
    'numbers',
    'numbers',
    'numbers',
    'numbers',
    'numbers',
    'numbers',
    'numbers',
    'numbers',
    'numbers',
    'numbers',
    'numbers',
    'numbers',
    'is_prize_taken',
    'prize',
]

MAPPING_FOR_DICT_W_NUMBERS = [
    'draw_date',
    'draw_num',
    'draw_stats_link',
    'number_1',
    'number_2',
    'number_3',
    'number_4',
    'number_5',
    'number_6',
    'number_7',
    'number_8',
    'number_9',
    'number_10',
    'number_11',
    'number_12',
    'is_prize_taken',
    'prize',
]


# 12x24 Результаты тиража № 1, 7 мая 2015 в 15:14
FIRST_DRAW_DAYS_AGO = delta_days('7 05 2015') + 1


class Lottery12x24Parser(DefaultLotteryParser):
    """Parser for 12x24 Lottery html's"""
    MAPPING_FOR_DICT = MAPPING_FOR_DICT
    MAPPING_FOR_DICT_W_NUMBERS = MAPPING_FOR_DICT_W_NUMBERS
    mapping = MAPPING_LOTTERY_HTML


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
