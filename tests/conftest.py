from collections import OrderedDict

import pytest

from stoloto.utils import sl_files

CURRENT_DIR = sl_files.get_dir(__file__)
HTML_MAINPAGE_FILENAME = CURRENT_DIR.joinpath('data/2020.02.22_page000001.txt')
HTML_PAGE2_FILENAME = CURRENT_DIR.joinpath('data/2020.02.22_page000002.txt')

RAPIDO_HTML_MAPPING = OrderedDict({
    'get_drawdate': 'div.draw_date',
    'get_draw': 'div.draw > a',
    'get_drawnumbers': 'div.numbers > div.numbers_wrapper > div.container.cleared > span.zone > b',
    'get_prize': 'div.prize',
    '_elements': 'div.month>div.elem>div.main',
})


@pytest.fixture
def main_page_text_content():
    with open(HTML_MAINPAGE_FILENAME, 'r') as file:
        return file.read()


@pytest.fixture
def page2_text_content():
    with open(HTML_PAGE2_FILENAME, 'r') as file:
        return file.read()
