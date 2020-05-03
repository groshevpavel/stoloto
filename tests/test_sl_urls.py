import pytest

from stoloto import StolotoArchiveUrls


def test__not_set_lottery_name():
    sl_urls = StolotoArchiveUrls()
    with pytest.raises(AssertionError):
        _ = sl_urls.main_archive_page_url
    with pytest.raises(AssertionError):
        _ = sl_urls.archive_page_url


def test__set_lottery_name():
    sl_urls = StolotoArchiveUrls(lottery_name='rapido2')

    assert sl_urls.main_archive_page_url == 'https://www.stoloto.ru/rapido2/archive'
    assert sl_urls.archive_page_url == 'https://www.stoloto.ru/draw-results/rapido2/load'
