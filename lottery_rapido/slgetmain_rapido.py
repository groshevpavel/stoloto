import asyncio
import time
from collections import OrderedDict

from lottery_rapido.config_rapido import LotteryConfig
from stoloto.http.sl_gd_async import StolotoGetdataAsync
from stoloto.utils import make_function_async, sl_files, date
from stoloto.utils.my_ordered_dict import MyOrderedDict
from stoloto.parsers.sl_rapido import LotteryRapidoParser as sl_parser


def sort_lottery_data(lottery_data, key=lambda draw: draw[1], reverse=True):
    sorted_ = sorted(lottery_data, key=key, reverse=reverse)
    print(f'Sorted {len(lottery_data)} records, reverse={reverse}')
    return sorted_


def find_out_which_lost(sorted_lottery_list_of_tuples: list):
    last_draw_number = sorted_lottery_list_of_tuples[0][1]
    if len(sorted_lottery_list_of_tuples) == last_draw_number:
        return sorted_lottery_list_of_tuples

    filename_parts = []
    for index, draw in enumerate(sorted_lottery_list_of_tuples[:-1]):
        draw_num = draw[1]
        prev_draw_num = sorted_lottery_list_of_tuples[index+1][1]

        if draw_num - prev_draw_num > 1:
            print(draw_num, prev_draw_num, draw[0])
            filename_part = '.'.join(draw[0].split()[0].split('.')[::-1])  # reverse date str to YYYY.MM.DD
            filename_parts.append(filename_part)

    list_of_filenames_to_parse = sl_files.get_archive_filenames(folder=LotteryConfig.ARCHIVE_PATH, in_filename=filename_parts)
    missed_draws_data = asyncio.run(asynchronous(list_of_filenames_to_parse))
    new_lottery_data = append_old_lottery_data(sorted_lottery_list_of_tuples, missed_draws_data)
    return sort_lottery_data(new_lottery_data)


def normalize_pickle_list_of_tuples(lottery_list_of_tuples: list) -> tuple:
    # 29.03.2020 10:37:30,180330,/rapido/archive/180330,False,-1,,,,,,,,,
    # 29.03.2020 10:37:30,180330,/rapido/archive/180330,5,12,16,18,7,15,14,3,4,False,583188
    new_lottery_data = []
    skipped = []
    for index, lottery_data in enumerate(lottery_list_of_tuples):
        if len(lottery_data) != len(sl_parser.MAPPING_FOR_DICT):
            skipped.append(lottery_data)
            print(f'Skipped, at index {index}: corrupted data: {lottery_data}')
            continue
        new_lottery_data.append(lottery_data)

    # TODO: list of skipped dates, for next retrieving draw data only for list of this
    skipped_days = set([archive_name_splitter_for_date(s) for s in skipped])
    return new_lottery_data, skipped_days


def load_old_lottery_data():
    lottery_data = sl_files.load_pickle(LotteryConfig.PICKLE_FN__LIST_OF_TUPLES)
    return normalize_pickle_list_of_tuples(lottery_data)


def append_old_lottery_data(old_lottery_data, new_lottery_data):
    old_lottery_data.extend(new_lottery_data)
    return list(set(old_lottery_data))


def save_lottery_data(lottery_data):
    lottery_data = sort_lottery_data(lottery_data)
    lottery_data = find_out_which_lost(lottery_data)

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
        return lottery_parsed_result, lottery_main_html_filename


async def asynchronous(list_of_filenames_to_parse, **kwargs):
    start = time.time()

    futures = [async_parse(fn) for fn in list_of_filenames_to_parse]

    exceptions = []
    new_lottery_data = []
    for i, future in enumerate(asyncio.as_completed(futures)):
        try:
            result = await future
            new_lottery_data.extend(result[0])
            print(i, len(result[0]), result[1])
        except Exception as e:
            print(f"Task {i}; Exception! {e}; result: {result}")
            exceptions.append((i, e, result,))

    if exceptions:
        print(f'Exceptions during parsing: {len(exceptions)}')
        for index, e, result in exceptions[:30]:
            print(f'Job: {index}: {e}; result: {result}')

    print('parsing took: {:.2f} seconds'.format(time.time() - start))
    print(f'Parsed {len(new_lottery_data)} records')

    return new_lottery_data


def archive_name_splitter_for_date(archive_filename, filename_splitter='_page') -> str:
    # D:\python\stoloto\lottery_rapido\archive\2020.03.28_page000001.txt
    archive_filename = str(archive_filename).split('\\')[-1]
    return archive_filename.split(filename_splitter)[0]


def days_between_oldest_archive_and_now(mapping: OrderedDict) -> int:
    oldest_filename = list(mapping)[0]
    oldest_filedate = mapping[oldest_filename]
    archive_delta_days = date.delta_days(oldest_filedate, date_format_str='%d.%m.%Y')

    if archive_delta_days == 0:
        archive_delta_days += 2
    print('Archive delta days:', archive_delta_days, 'for:', oldest_filename)
    return archive_delta_days


def filename_to_date_mapping(archive_folder=LotteryConfig.ARCHIVE_PATH) -> dict:
    res = OrderedDict()
    sorted_ = sorted(sl_files.get_archive_filenames(archive_folder, in_filename='page'), reverse=True)
    for fn in sorted_:
        date_filename_str = archive_name_splitter_for_date(fn)
        date_filename = date.guess_format(date_filename_str, date_format_str=date.DateFormat.YMD_DOTTED)
        res[fn] = date_filename
    return res


if __name__ == '__main__':
    from myhdrs import headers_dict_from_str

    old_lottery_data, skipped_lottery_days = load_old_lottery_data()

    mapping = filename_to_date_mapping()
    archive_delta_days = days_between_oldest_archive_and_now(mapping)

    s = StolotoGetdataAsync(
        max_concurrency=LotteryConfig.SLGD_MAX_CONCURRENCY,
        archive_filename_date_format='%Y.%m.%d',
        headers=headers_dict_from_str()
    )

    s.start(
        lottery_name=LotteryConfig.LOTTERY_NAME,
        fn_prefix='./archive/{archive_date}_page{page_num}.txt',
        archive_days_ago=archive_delta_days,
    )

    # '28.03.2020 21:07:30'
    lottery_draw_dates_in_pickle = set([lottery[0].split(' ')[0] for lottery in old_lottery_data])
    lottery_draw_dates_in_pickle = [
        date.guess_format(lottery_date) for lottery_date in lottery_draw_dates_in_pickle
        if lottery_date != date.today()
    ]

    list_of_filenames_to_parse = [
        fn for fn, archive_date in mapping.items()
        if archive_date not in lottery_draw_dates_in_pickle
    ]
    # TODO: rewrite in threads
    new_lottery_data = asyncio.run(asynchronous(list_of_filenames_to_parse))
    save_lottery_data(append_old_lottery_data(old_lottery_data, new_lottery_data))
