from collections import OrderedDict


# key is func name in parser class that will call for post-processing html result,
# that was extracted by css rule in value
MAPPING_LOTTERY_HTML = OrderedDict({
    'get_drawdate': 'div.draw_date',
    'get_draw': 'div.draw > a',
    'get_drawnumbers': 'div.numbers > div.numbers_wrapper > div.container.cleared > span.zone > b',
    'get_prize': 'div.prize',
    '_elements': 'div.month>div.elem>div.main',
})

MAPPING_FOR_DICT = [
    # map for Rapido One
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
    'is_prize_taken',
    'prize',
]

MAPPING_FOR_DICT_W_NUMBERS = [
    # map for Rapido One
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
    'is_prize_taken',
    'prize',
]
