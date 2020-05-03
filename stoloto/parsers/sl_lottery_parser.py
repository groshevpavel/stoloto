import lxml.html
from cssselect import GenericTranslator


class BaseLotteryParser(object):
    def __init__(self, html_fn=None, html_content=None, mapping=None):
        if html_fn is None and html_content is None:
            raise ValueError(
                'Need html content in "html_content=" param, or html filename in "html_fn=" param'
            )
        self.html_fn, self.html_content = html_fn, html_content

        if mapping is not None:
            self.mapping = mapping

        self.res = []

    def __list__(self):
        return list(self.start())

    def __iter__(self):
        return self.start()

    def start(self, root_css_keyname_in_mapping='_elements'):
        lottery_all_draws_html = self.html_parse()
        elements_css = self.mapping.get(root_css_keyname_in_mapping)
        all_lottery_draws_root_elements = self.get_by_css(lottery_all_draws_html, elements_css)
        return self.get_all_parsed_draws(all_lottery_draws_root_elements)

    def get_all_parsed_draws(self, all_lottery_draws_root_elements):
        all_parsed_draws = []
        for draw_data in self.yield_one_draw_data(all_lottery_draws_root_elements):
            all_parsed_draws.append(draw_data)
        return all_parsed_draws

    def yield_one_draw_data(self, elements):
        """Walk all elements in mapping dict and yield by one tuple of lottery draw details"""
        for lottery_draw_root_html in elements:
            result = []
            for lottery_detail in self.get_lottery_details(lottery_draw_root_html):
                result.extend(lottery_detail if isinstance(lottery_detail, (list, tuple,)) else tuple([lottery_detail]))
            yield tuple(result)

    def get_lottery_details(self, lottery_draw_root_element):
        """Walk all not dunder-starting keys of mapping dict
         and get draw data by css rule from mapping.value,
         then post-process it by self.mapping.key procedure(if self has it)"""
        for k, v in self.mapping.items():
            if k.startswith('_'):
                continue
            if not hasattr(self, k):
                setattr(self, k, self.get_by_css(lottery_draw_root_element, v))
            if hasattr(self, k):
                attr = getattr(self, k)
                if callable(attr):
                    yield attr(self.get_by_css(lottery_draw_root_element, v))
                else:
                    yield attr

    def html_parse(self):
        if self.html_fn:
            if not isinstance(self.html_fn, str):
                self.html_fn = str(self.html_fn)
            document = lxml.html.parse(self.html_fn)
        elif self.html_content:
            document = lxml.html.fromstring(self.html_content)
        return document

    @classmethod
    def get_by_css(cls, el, css_rule):
        xpath_text = cls.get_xpath_text(css_rule)
        return el.xpath(xpath_text)

    @staticmethod
    def get_xpath_text(css_text):
        return GenericTranslator().css_to_xpath(css_text)


class DefaultLotteryParser(BaseLotteryParser):
    """It's default lottery parser that has def css parsing methods applicable to most lottery archive pages.
    In fact it is only container for parse static methods. All machinery placed in BaseLotteryParser"""
    MAPPING_FOR_DICT = None
    MAPPING_FOR_DICT_W_NUMBERS = None
    mapping = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_draw(el):
        """Возвращает tuple - номер тиража, ссылку на подробности по этому тиражу"""
        if len(el) > 1:
            raise Exception(f"Обнаружено изменение исходного html ({repr(el)})")

        draw_no = int(el[0].text)
        return draw_no, el[0].get('href')

    @staticmethod
    def get_drawdate(draw_date_el):
        """Возвращает строку - дату тиража"""
        if len(draw_date_el) > 1:
            raise Exception("Обнаружено изменение исходного html")

        return draw_date_el[0].text

    @staticmethod
    def get_drawnumbers(el):
        """Получаем номера тиража"""
        return [int(e.text) for e in el]

    @staticmethod
    def get_prize(el):
        """
            Получаем статиситку тиража
            Розыграны ли: суперприз, приз
            Суммы: суперприза, приза

            Возвр: кортеж (розыгран суперприз?, сумма суперприза, розыгран приз?, сумма приза)
        """
        is_prize_taken = bool(el[0].find_class('with_jackpot'))

        prize_div = el[0].text_content().split(',')[0]
        prize_nums = list(filter(lambda c: c in list('0123456789'), prize_div))

        prize = -1
        if prize_nums:
            prize = int(''.join(prize_nums))

        # superprize_div_jackpot_wrapper = el[0]
        # spans_jackpot_wrapper = superprize_div_jackpot_wrapper.getchildren()
        # is_superprize_taken = bool(spans_jackpot_wrapper[0].text_content())
        # superprize = int(''.join(list(filter(str.isdigit, spans_jackpot_wrapper[1].text_content()))))

        return is_prize_taken, prize
