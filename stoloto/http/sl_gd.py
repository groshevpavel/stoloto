import requests
from lxml import html
from lxml import etree

from cssselect import GenericTranslator, SelectorError

import csv
import datetime

from time import sleep

from os.path import dirname, abspath, join, exists, splitext, basename
from os import makedirs

from stoloto.utils.date import today


class SLGD(object):
    """
        StoLoto Get Data
    """

    def __init__(self,
                 urls=(None, None),  # main url, archive_url
                 lottery_name=None,  # lottery name for name of directory to save retrieved html data
                 lottery_name_dir=None,  # if specified will used as html save directory name
                 lottery_archive_name_dir=None,  # dir name where stored lottery archive htmls
                 ):
        self.main_url, self.archive_url = urls
        if not self.main_url or not self.archive_url:
            raise ValueError('Need to specify urls=(main_lottery_url, archive_lottery_url,)')

        if not lottery_name:
            raise ValueError("Need to specify Lottery name for name of directory to save html data")
        self.lottery_name = self.lottery_name_dir = lottery_name
        if lottery_name_dir is not None:
            self.lottery_name_dir = lottery_name_dir
        if lottery_archive_name_dir is not None:
            self.lottery_archive_name_dir = lottery_archive_name_dir
        else:
            self.lottery_archive_name_dir = join(self.lottery_name_dir, 'archive')

        self.headers = get_hdict(headers_str)
        self.proxies = None
        self.session = None



        self.url6x45main = "https://www.stoloto.ru/6x45/archive"
        self.url6x45archive = "https://www.stoloto.ru/draw-results/6x45/load"

        self.url7x49main = "https://www.stoloto.ru/7x49/archive"
        self.url7x49archive = "https://www.stoloto.ru/draw-results/7x49/load"

        self.rapido2archive = 'https://www.stoloto.ru/rapido2/archive'
        self.rapido2main = 'https://www.stoloto.ru/rapido2/archive'


    def r(self, method, url, **kw):
        if not self.session:
            self.session = requests.Session()

        # print(self.headers)
        r = self.session.request(method, url, headers=self.headers, proxies=self.proxies, timeout=10, verify=True,
                                 **kw)
        return r

    def get(self, url, **kw):
        return self.r('GET', url, **kw)

    def post(self, url, **kw):
        return self.r('POST', url, **kw)

    def get_main(self):
        r = self.get(self.main_url)
        # default_headers = urllib3.make_headers(proxy_basic_auth='groshev_pp:UUUUuuuu2312')
        # http = urllib3.ProxyManager("https://mwg.corp.tander.ru:3128/", headers=default_headers)

        # url = "https://www.google.com/"
        # r = http.request('GET', url, headers=headers_)
        # r = http.request('GET', url, headers=headers_, proxies=proxies)

        # print(dir(r))
        # print(r.status_code, r.content)
        document = html.fromstring(r.content)

        main_xpath = GenericTranslator().css_to_xpath('div.month')

        res = document.xpath(main_xpath)

        # assert len(res) == 1, 'Изменилась структура html'

        res_str = ""
        for r in res:
            res_str += etree.tostring(r, pretty_print=True).decode('utf-8')
            res_str += "\n"
        return res_str

    def save_main(self):
        inner_html = self.get_main()
        filename_saved_main_lottery_page = savefile(f"{self.lottery_name_dir}\\page1.txt", inner_html)
        print(f'"{self.lottery_name}" lottery html saved into: {filename_saved_main_lottery_page}')
        return filename_saved_main_lottery_page

    def get_archive7x49(self, **kw):
        return self.get_archive(self.url7x49archive, **kw)

    def get_archive6x45(self, **kw):
        return self.get_archive(self.url6x45archive, **kw)

    def get_archive5x36(self, **kw):
        return self.get_archive(self.url5x36archive, **kw)

    def get_archive(self, url=None, page=2, start_archive_date=today(1800), to=today()):
        form['to'] = to
        form['from'] = start_archive_date
        form['page'] = page
        # form['searchBy'] = 'date'
        # form['withSuperprize'] = 'false'

        if not url:
            url = self.archive_url
        r = self.post(url, data=form)
        j = r.json()
        # htmlraw = r.content

        return j

        # tree = html.fromstring(htmlraw)

    def yield_archive_page(self, selfmethod, start=2, end=999, stop='stop', data='data', status='status',
                           status_ok='ok', sleep_secs=0.5, **kw):

        page = start
        while True:
            if page > end: break

            j = selfmethod(page=page, **kw)
            if j[status] != status_ok or j[stop]:
                return

            yield j[data], page
            page += 1

            sleep(sleep_secs)

    def save_archive_raw(self, get_archive_method=None, **kw) -> list:
        """Get archive html data and save into .txt file
        returns: list of saved file names"""
        if get_archive_method is None:
            get_archive_method = self.get_archive
        files = []
        for page_data, page_no in self.yield_archive_page(get_archive_method, **kw):
            if not page_data:
                break
            fn = savefile(f'{self.lottery_archive_name_dir}\\page{page_no}.txt', page_data)
            files.append(fn)
            sleep(0.5)
            print(page_no, len(page_data))
        return files


if __name__ == "__main__":
    pass
    # s = SLGD()
    # s.save_main5x36()
    # s.save_archive(s.get_archive5x36, end=5)
    # s.save_archive(s.get_archive5x36)

    # s.save_main6x45()
    # s.save_archive(s.get_archive6x45)

    # s.save_main7x49()
    # s.save_archive(s.get_archive7x49)
