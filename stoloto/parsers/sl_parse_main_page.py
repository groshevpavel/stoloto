from cssselect import GenericTranslator
from lxml import html, etree


def parse_main_page(response_text: str):
    # TODO: Find out necessity, delete all commented lines and comb
    # default_headers = urllib3.make_headers(proxy_basic_auth='groshev_pp:UUUUuuuu2312')
    # http = urllib3.ProxyManager("https://mwg.corp.tander.ru:3128/", headers=default_headers)

    # url = "https://www.google.com/"
    # r = http.request('GET', url, headers=headers_)
    # r = http.request('GET', url, headers=headers_, proxies=proxies)

    # print(dir(r))
    # print(r.status_code, r.content)
    document = html.fromstring(response_text)

    main_xpath = GenericTranslator().css_to_xpath('div.month')

    res = document.xpath(main_xpath)

    # assert len(res) == 1, 'Изменилась структура html'

    res_str = ""
    for r in res:
        res_str += etree.tostring(r, pretty_print=True).decode('utf-8')
        res_str += "\n"
    return res_str