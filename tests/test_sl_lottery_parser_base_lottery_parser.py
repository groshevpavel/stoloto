import types

import lxml
import pytest

from stoloto.parsers.sl_lottery_parser import BaseLotteryParser
from tests import conftest


def test_not_valid_init():
    with pytest.raises(ValueError):
        _ = BaseLotteryParser()


def test_valid_init_with_html_fn():
    lottery_parser = BaseLotteryParser(html_fn=conftest.HTML_MAINPAGE_FILENAME)
    assert isinstance(lottery_parser, BaseLotteryParser)


def test_valid_init_with_html_content(main_page_text_content):
    lottery_parser = BaseLotteryParser(html_content=main_page_text_content)
    assert isinstance(lottery_parser, BaseLotteryParser)


def test_html_parse_from_html_fn():
    lottery_parser = BaseLotteryParser(html_fn=conftest.HTML_MAINPAGE_FILENAME)
    document = lottery_parser.html_parse()

    assert isinstance(document, lxml.etree._ElementTree)


def test_html_parse_from_html_content(page2_text_content):
    lottery_parser = BaseLotteryParser(html_content=page2_text_content)
    document = lottery_parser.html_parse()

    assert isinstance(document, lxml.html.HtmlElement)


def test_get_by_css_from_html_fn():
    lottery_parser = BaseLotteryParser(html_fn=conftest.HTML_MAINPAGE_FILENAME)
    document = lottery_parser.html_parse()
    elements = lottery_parser.get_by_css(document, conftest.RAPIDO_HTML_MAPPING['_elements'])

    assert isinstance(elements, (tuple, list,))
    assert len(elements) == 50
    assert isinstance(elements[-1], lxml.html.HtmlElement)
    assert elements[-1].attrib == {'class': 'main'}


def test_get_xpath_text_from_html_fn():
    lottery_parser = BaseLotteryParser(html_fn=conftest.HTML_MAINPAGE_FILENAME)
    xpath = lottery_parser.get_xpath_text(conftest.RAPIDO_HTML_MAPPING['_elements'])

    assert isinstance(xpath, str), type(xpath)
    assert xpath == """descendant-or-self::div[@class and contains(concat(' ', normalize-space(@class), ' '), ' month ')]/div[@class and contains(concat(' ', normalize-space(@class), ' '), ' elem ')]/div[@class and contains(concat(' ', normalize-space(@class), ' '), ' main ')]"""


def test_start__error_no_mapping():
    lottery_parser = BaseLotteryParser(html_fn=conftest.HTML_MAINPAGE_FILENAME)

    with pytest.raises(AttributeError):  # self.mapping not initialized
        _ = lottery_parser.start()


def test_start__no_error_with_mapping(page2_text_content):
    lottery_parser = BaseLotteryParser(html_content=page2_text_content, mapping=conftest.RAPIDO_HTML_MAPPING)
    parser_generator = lottery_parser.start()
    assert isinstance(parser_generator, types.GeneratorType)

    first_draw = next(parser_generator)
    assert isinstance(first_draw, (tuple, list,)), first_draw
    assert len(first_draw) == 12

    assert first_draw[0].attrib == {'class': 'draw_date', 'title': '22.02.2020 07:22:30'}
    assert first_draw[1].attrib == {'href': '/rapido/archive/177084'}

    assert first_draw[2].attrib == {}
    assert first_draw[2].text == '10\xa0'
    assert first_draw[-2].attrib == {'class': 'extra'}
    assert first_draw[-2].text == '4\xa0'

    assert first_draw[-1].attrib == {'class': 'prize '}
    assert '3\xa0980\xa0508' in first_draw[-1].text
