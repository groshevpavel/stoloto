import asyncio
import time
from collections import OrderedDict

from lottery_12x24.config_12x24 import LotteryConfig
from stoloto.http.sl_gd_async import StolotoGetdataAsync
from stoloto.utils import make_function_async, sl_files
from stoloto.utils.my_ordered_dict import MyOrderedDict
from stoloto.parsers.sl_12x24 import Lottery12x24Parser as sl_parser


def sort_lottery_data(lottery_data, key=lambda draw: draw[1], reverse=True):
    sorted_ = sorted(lottery_data, key=key, reverse=reverse)
    print(f'Sorted {len(lottery_data)} records, reverse={reverse}')
    return sorted_


def append_old_lottery_data(new_lottery_data):
    old_lottery_data = sl_files.load_pickle(LotteryConfig.PICKLE_FN__LIST_OF_TUPLES)
    old_lottery_data.extend(new_lottery_data)
    return list(set(old_lottery_data))


def save_lottery_data(lottery_data):
    lottery_data = append_old_lottery_data(lottery_data)
    lottery_data = sort_lottery_data(lottery_data)

    sl_files.save_pickle(LotteryConfig.PICKLE_FN__LIST_OF_TUPLES, lottery_data)

    draws_dict = [OrderedDict(zip(sl_parser.MAPPING_FOR_DICT_W_NUMBERS, r)) for r in lottery_data]
    sl_files.save_csv(LotteryConfig.CSV_FILENAME_LOTTERY_DATA, draws_dict, delimiter=',')

    draws_dict = [MyOrderedDict(zip(sl_parser.MAPPING_FOR_DICT, r)) for r in lottery_data]
    sl_files.save_pickle(LotteryConfig.PICKLE_FN__LIST_OF_DICTS_NUMBERS, draws_dict)


async def async_parse(lottery_main_html_filename: str):
    async with asyncio.BoundedSemaphore(LotteryConfig.PARSE_MAX_CONCURRENCY):
        parser = sl_parser(html_fn=lottery_main_html_filename)
        async_parse_func = make_function_async(parser.start)
        lottery_parsed_result = await async_parse_func()
        return lottery_parsed_result


async def asynchronous(*args, **kwargs):
    start = time.time()

    futures = [
        async_parse(fn)
        for fn in sl_files.get_archive_filenames(kwargs.pop('folder'), in_filename=kwargs.pop('str_in_filename'))
    ]

    lottery_data = []
    for i, future in enumerate(asyncio.as_completed(futures)):
        try:
            result = await future
            lottery_data.extend(result)
            print(i, len(result))
        except Exception as e:
            print(f"Task {i}; Exception! {e}")

    print('parsing took: {:.2f} seconds'.format(time.time() - start))
    print(f'Parsed {len(lottery_data)} records')

    save_lottery_data(lottery_data)


if __name__ == '__main__':
    from myhdrs import headers_dict_from_str

    s = StolotoGetdataAsync(
        max_concurrency=LotteryConfig.SLGD_MAX_CONCURRENCY,
        archive_filename_date_format='%Y.%m.%d',
        headers=headers_dict_from_str()
    )
    s.start(
        lottery_name=LotteryConfig.LOTTERY_NAME,
        fn_prefix='./archive/{archive_date}_page{page_num}.txt',
        archive_days_ago=LotteryConfig.GET_ARCHIVE_DAYS_AGO,
    )

    asyncio.run(
        asynchronous(
            folder=LotteryConfig.ARCHIVE_PATH,
            str_in_filename=LotteryConfig.STR_IN_FILENAME,
        )
    )
