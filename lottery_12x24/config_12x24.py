from stoloto.parsers.sl_12x24 import FIRST_DRAW_DAYS_AGO
from stoloto.utils import sl_files
from stoloto.utils.date import today


class LotteryConfig:
    LOTTERY_NAME = '12x24'

    LOTTERY_ROOT_DIR = sl_files.get_dir(__file__)

    ARCHIVE_PATH = LOTTERY_ROOT_DIR.joinpath('archive')
    sl_files.check_and_create_dirs(ARCHIVE_PATH)

    PICKLE_PATH = LOTTERY_ROOT_DIR.joinpath('pickle')
    sl_files.check_and_create_dirs(PICKLE_PATH)

    CSV_PATH = LOTTERY_ROOT_DIR.joinpath('csv')
    sl_files.check_and_create_dirs(CSV_PATH)

    PICKLE_FN__LIST_OF_TUPLES = PICKLE_PATH.joinpath(f'archive_{LOTTERY_NAME}_list_of_tuples.pickle')
    PICKLE_FN__LIST_OF_DICTS_NUMBERS = PICKLE_PATH.joinpath(f'archive_{LOTTERY_NAME}_list_of_dicts_numbers.pickle')
    CSV_FILENAME_LOTTERY_DATA = CSV_PATH.joinpath(f'archive_{LOTTERY_NAME}.csv')

    PARSE_MAX_CONCURRENCY = 50
    SLGD_MAX_CONCURRENCY = 2

    GET_ARCHIVE_DAYS_AGO = 1000 if sl_files.check_exist(CSV_FILENAME_LOTTERY_DATA) else FIRST_DRAW_DAYS_AGO
    STR_IN_FILENAME = today(date_format='%Y.%m.%d') if sl_files.check_exist(CSV_FILENAME_LOTTERY_DATA) else ''