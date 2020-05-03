import asyncio
import time

from stoloto.http.sl_gd import SLGD
from stoloto.parsers.sl_rapido2 import Rapido2LotteryParser as sl_parser
from collections import OrderedDict

from stoloto.utils import make_function_async, sl_files
from stoloto.utils.my_ordered_dict import MyOrderedDict

LOTTERY_NAME = 'rapido2'

URL_MAIN = 'https://www.stoloto.ru/rapido2/archive'
URL_ARCHIVE = 'https://www.stoloto.ru/draw-results/rapido2/load'

LOTTERY_ROOT_DIR = sl_files.get_dir(__file__)

PICKLE_FN__LIST_OF_TUPLES = LOTTERY_ROOT_DIR.joinpath(f'{LOTTERY_NAME}/pickle/archive_{LOTTERY_NAME}_list_of_tuples.pickle')
PICKLE_FN__LIST_OF_DICTS_NUMBERS = LOTTERY_ROOT_DIR.joinpath(f'{LOTTERY_NAME}/pickle/archive_{LOTTERY_NAME}_list_of_dicts_numbers.pickle')
CSV_FILENAME_LOTTERY_DATA = LOTTERY_ROOT_DIR.joinpath(f'{LOTTERY_NAME}/csv/archive_{LOTTERY_NAME}.csv')
ARCHIVE_PATH = LOTTERY_ROOT_DIR.joinpath(LOTTERY_NAME, 'archive', )

MAX_CONCURRENCY = 50

slgd = SLGD(urls=(URL_MAIN, URL_ARCHIVE), lottery_name=LOTTERY_NAME)


def sort_lottery_data(lottery_data, key=lambda draw: draw[1], reverse=True):
    print(f'Sorted, key={key}, reverse={reverse}')
    return sorted(lottery_data, key=key, reverse=reverse)


def save_lottery_data(lottery_data):
    sl_files.save_pickle(PICKLE_FN__LIST_OF_TUPLES, lottery_data)

    draws_dict = [OrderedDict(zip(sl_parser.mapping_for_dict_w_numbers, r)) for r in lottery_data]
    sl_files.save_csv(CSV_FILENAME_LOTTERY_DATA, draws_dict, delimiter=',')

    draws_dict = [MyOrderedDict(zip(sl_parser.mapping_for_dict, r)) for r in lottery_data]
    sl_files.save_pickle(PICKLE_FN__LIST_OF_DICTS_NUMBERS, draws_dict)


def get_last():
    """get last page draw results"""
    lottery_main_html_filename = slgd.save_main()
    lottery_parsed_result = sl_parser(fn=lottery_main_html_filename).start()
    lottery_old_data = sl_files.load_pickle(PICKLE_FN__LIST_OF_TUPLES)

    records_added_count = 0
    for draw_data in lottery_parsed_result:
        if draw_data in lottery_old_data:
            continue
        lottery_old_data.append(draw_data)
        records_added_count += 1
    print(f'added: {records_added_count} records')

    return lottery_old_data


def get_parse_save_archive(**kwargs):
    files = slgd.save_archive_raw(**kwargs)  # save all archive into html .txt files
    lottery_data = sl_files.parse_archive_files(files, lottery_parser_class=sl_parser)
    sorted_lottery_data = sort_lottery_data(lottery_data)
    save_lottery_data(sorted_lottery_data)


def save_last():
    lottery_data = get_last()
    sorted_lottery_data = sort_lottery_data(lottery_data)
    save_lottery_data(sorted_lottery_data)


def async_start(*args, **kwargs):
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(asynchronous(*args, **kwargs))
    finally:
        # loop.run_until_complete(asyncio.sleep(0.250))
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()


async def asynchronous(*args, **kwargs):
    start = time.time()
    folder = kwargs.pop('folder')
    futures = [async_parse(fn) for fn in sl_files.get_archive_filenames(folder)]

    lottery_data = []
    for i, future in enumerate(asyncio.as_completed(futures)):
        # try:
        #     result = await future
        #     print(i, result)
        # except Exception as e:
        #     print(f"Exception! {e}")
        result = await future
        lottery_data.extend(result)
        print(i, len(result))

    print('took: {:.2f} seconds'.format(time.time() - start))

    sorted_lottery_data = sort_lottery_data(lottery_data)
    save_lottery_data(sorted_lottery_data)


async def async_parse(lottery_main_html_filename: str):
    async with asyncio.BoundedSemaphore(MAX_CONCURRENCY):
        parser = sl_parser(fn=lottery_main_html_filename)
        async_parse_func = make_function_async(parser.start)
        lottery_parsed_result = await async_parse_func()
        return lottery_parsed_result


if __name__ == '__main__':
    # get_parse_save_archive(end=5)
    # save_last()
    async_start(folder=ARCHIVE_PATH)
