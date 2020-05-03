import lxml.html
from cssselect import GenericTranslator, SelectorError

from collections import OrderedDict


lottery_html_mapping = OrderedDict({
    'get_drawdate': 'div.draw_date',
    'get_draw': 'div.draw > a',
    'get_drawnumbers': 'div.numbers > div.numbers_wrapper > div.container.cleared > span.zone > b',
    'get_prize': 'div.prize',
    '_elements': 'div.month>div.elem>div.main',
})

mapping_for_dict = [
    # ('24.02.2019 15:00', 9885, '/5x36plus/archive/9885', 14, 33, 28, 8, 21, 4, False, 4656632, False, 3756780)
    'draw_date'
    , 'draw_num'
    , 'draw_stats_link'
    , 'numbers'
    , 'numbers'
    , 'numbers'
    , 'numbers'
    , 'numbers'
    # ,'number_1'
    # ,'number_2'
    # ,'number_3'
    # ,'number_4'
    # ,'number_5'
    , 'number_extra'
    , 'is_superprize_taken'
    , 'superprize'
    , 'is_prize_taken'
    , 'prize'
]
mapping_for_dict_w_numbers = [
    # ('24.02.2019 15:00', 9885, '/5x36plus/archive/9885', 14, 33, 28, 8, 21, 4, False, 4656632, False, 3756780)
    'draw_date'
    , 'draw_num'
    , 'draw_stats_link'
    , 'number_1'
    , 'number_2'
    , 'number_3'
    , 'number_4'
    , 'number_5'
    , 'number_6'
    , 'number_7'
    , 'number_8'
    , 'number_9'
    , 'is_prize_taken'
    , 'prize'
]
# Результаты тиража № 1, 13 мая 2019 в 13:05 // https://www.stoloto.ru/rapido2/archive/1
FIRST_DRAW_DAYS_AGO_RAPIDO2 = delta_days('13 05 2019') + 1

class LotteryParser(object):
    def __init__(self, fn=None, html=None, mapping=lottery_html_mapping):
        if not fn and not html:
            raise ValueError(
                "Необходимо задать имя файла с html кодом в параметре 'fn' или передать сам текст html-кода в параметре 'html'")

        self.mapping = mapping
        document = lxml.html.parse(str(fn)) if fn else lxml.html.fromstring(html)
        self.els = self.get_by_css(document, self.mapping.get('_elements'))
        self.res = None

        # del self.document

    def __len__(self):
        return len(self.res) if self.res is not None else len(self.els)

    def __list__(self):
        return self.start()

    def __iter__(self):
        if not hasattr(self, 'res') or self.res is None:
            return iter(self.start())
        else:
            return iter(self.res)

    def start(self):
        self.res = []
        for e in self.els:
            _r = []
            for d in self.get_data(e):
                _r.extend(d if isinstance(d, (list, tuple,)) else tuple([d]))
            self.res.append(tuple(_r))
        return self.res

    @classmethod
    def get_data(cls, e):
        for k, v in lottery_html_mapping.items():
            if k.startswith('_'): continue
            if not hasattr(cls, k):
                setattr(cls, k, cls.get_by_css(v))
            if hasattr(cls, k):
                attr = getattr(cls, k)
                if callable(attr):
                    yield attr(cls.get_by_css(e, v))
                else:
                    yield attr

    @staticmethod
    def get_xpath_text(csstext):
        return GenericTranslator().css_to_xpath(csstext)

    @classmethod
    def get_by_css(cls, el, css_rule):
        xpathtext = cls.get_xpath_text(css_rule)
        return el.xpath(xpathtext)


class Rapido2LotteryParser(LotteryParser):
    """It's only container for parse methods. All magic placed in LotteryParser class"""
    mapping_for_dict = mapping_for_dict
    mapping_for_dict_w_numbers = mapping_for_dict_w_numbers

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_draw(el):
        """
            Возвращает tuple - номер тиража, ссылку на подробности по этому тиражу
        """
        if len(el) > 1:
            raise Exception(f"Обнаружено изменение исходного html ({repr(el)})")

        draw_no = int(el[0].text)
        return draw_no, el[0].get('href')

    @staticmethod
    def get_drawdate(draw_date_el):
        """
            Возвращает строку - дату тиража
        """
        if len(draw_date_el) > 1:
            raise Exception("Обнаружено изменение исходного html")

        return draw_date_el[0].text

    @staticmethod
    def get_drawnumbers(el):
        """
            Получаем номера тиража
        """
        return [int(e.text) for e in el]

    @staticmethod
    def get_prize(el):
        """
            Получаем статиситку тиража
            Розыграны ли: суперприз, приз
            Суммы: суперприза, приза
            
            Возвр: кортеж (розыгран суперприз?, сумма суперприза, розыгран приз?, сумма приза)
        """
        prize_div = el[0].text_content()
        is_prize_taken = bool(el[0].find_class('with_jackpot'))
        # prize_nums = list(filter(str.isdigit, prize_div))
        prize_nums = list(filter(lambda c: c in list('0123456789'), prize_div))
        prize = -1
        if prize_nums:
            prize = int(''.join(prize_nums))

        # superprize_div_jackpot_wrapper = el[0]
        # spans_jackpot_wrapper = superprize_div_jackpot_wrapper.getchildren()
        # is_superprize_taken = bool(spans_jackpot_wrapper[0].text_content())
        # superprize = int(''.join(list(filter(str.isdigit, spans_jackpot_wrapper[1].text_content()))))

        return is_prize_taken, prize


if __name__ == '__main__':
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
    pass
