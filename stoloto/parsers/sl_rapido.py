from stoloto.parsers import MAPPING_LOTTERY_HTML, MAPPING_FOR_DICT, MAPPING_FOR_DICT_W_NUMBERS
from stoloto.parsers.sl_lottery_parser import DefaultLotteryParser
from stoloto.utils.date import delta_days


# rapido Результаты тиража № 1, 25 марта 2013 в 20:00 // https://www.stoloto.ru/rapido/archive/1
FIRST_DRAW_DAYS_AGO = delta_days('25 03 2013') + 1


class LotteryRapidoParser(DefaultLotteryParser):
    """Parser for Rapido One Lottery html's"""
    MAPPING_FOR_DICT = MAPPING_FOR_DICT
    MAPPING_FOR_DICT_W_NUMBERS = MAPPING_FOR_DICT_W_NUMBERS
    mapping = MAPPING_LOTTERY_HTML


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


if __name__ == '__main__':
    # pass

    lottery_main_html_filename = '../../rapido/archive/2020.02.22_page000001.txt'
    lottery_parsed_result = LotteryRapidoParser(html_fn=lottery_main_html_filename).start()
    print(next(lottery_parsed_result))

    # res = []
    # for fn in get_archive_filenames():
    # fn = join(datapath, fn)
    # print(fn)
    # r = Parse5x36(fn)
    # rr = r.start()
    # res.extend(rr)
    # print(f"{len(res)}/{len(rr)}\t{fn}")

    # save_pickle('archive5x36_listOFtuples.pickle', res)
    # draws_dict = [OrderedDict(zip(_mapping_for_dict_w_numbers, r)) for r in res]

    # save_pickle('archive5x36_listOFdictsNUMBERS.pickle', draws_dict)
    # savecsv("archive5x36.csv", draws_dict)
