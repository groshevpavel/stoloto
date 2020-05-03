import asyncio
import random
import time

import aiofiles
import aiohttp

from stoloto.parsers.sl_parse_main_page import parse_main_page
from stoloto.utils.date import today
from stoloto.http.sl_urls import StolotoArchiveUrls


async def save_archive(fn, data, writemode='w', encoding='utf-8'):
    if len(data) < 1:
        return

    async with aiofiles.open(fn, writemode, encoding=encoding) as f:
        await f.write(data)


class StolotoGetdataAsync(StolotoArchiveUrls):
    """
        StoLoto Get Data Asynchronous version
    """
    def __init__(self,
                 login=None,
                 password=None,
                 max_concurrency=5,
                 **kwargs
                 ):
        self.session = None
        self.semaphore = asyncio.BoundedSemaphore(max_concurrency)

        self.auth = None
        if login and password:
            self.auth = aiohttp.BasicAuth(login, password)

        self.parse_main_page_func = kwargs.pop('parse_main_page_func', parse_main_page)
        self.archive_filename_date_format = kwargs.pop('archive_filename_date_format', '%Y%m%d')

        self.headers = kwargs.pop('headers', dict())

    def get_session(self, **kwargs):
        if self.session is None:
            if 'headers' in kwargs:
                self.session = aiohttp.ClientSession(headers=kwargs.pop('headers'))
            elif self.headers is not None:
                self.session = aiohttp.ClientSession(headers=self.headers)

            if self.auth:
                self.session = aiohttp.ClientSession(auth=self.auth)

        assert self.session, "Session not initialized!"
        assert isinstance(self.session, aiohttp.ClientSession), f"Session incorrectly initialized: {self.session}"

    async def r(self, method, url, **kwargs):
        self.get_session(**kwargs)

        as_json = kwargs.pop('as_json', False)

        async with self.semaphore:
            async with self.session.request(method, url, **kwargs) as response:
                if response.status == 200:
                    if as_json:
                        try:
                            return await response.json()
                        except aiohttp.client_exceptions.ContentTypeError:
                            return await response.json(content_type='')
                    else:
                        return await response.text()
                else:
                    raise ValueError(f'Bad response: {response.status} for {method} {url} {kwargs}')

    async def get(self, url, **kwargs):
        return await self.r('GET', url, **kwargs)

    async def post(self, url, **kwargs):
        return await self.r('POST', url, **kwargs)

    async def refresh_drawtime(self, **kwargs):
        fastgames_drawtime = await self.get(self.fastgames_draw_time_url, as_json=True, **kwargs)
        assert fastgames_drawtime.get('status') == 'ok', \
            f'Refresh fast games draw time failed! with {fastgames_drawtime}'
        assert 'games' in fastgames_drawtime and fastgames_drawtime.get('games') is not None,\
            f'Lottery draw time retrieve failed! with {fastgames_drawtime}'
        return fastgames_drawtime.pop('games')

    async def get_archive(
            self,
            page=2,
            start_archive_date=today(1),
            to=today(),
            **kwargs
    ):
        form = {'to': to, 'from': start_archive_date, 'page': page} if 'form' not in kwargs else kwargs.pop('form')
        url = self.archive_page_url if 'url' not in kwargs else kwargs.pop('url')
        if page > 1:
            return await self.post(url, data=form, as_json=True, **kwargs)
        # get main archive page with different method
        content = await self.get(self.main_archive_page_url, params=form, as_json=False, **kwargs)
        return {'data': self.parse_main_page_func(content), 'status': 'ok', 'stop': False}

    async def yield_archive_page(
            self,
            self_method=None,
            start_page=2,
            end_page=999,
            stop='stop',
            data='data',
            status='status',
            status_ok='ok',
            sleep_secs=0.3,
            **kwargs
     ):
        self_method = self.get_archive if self_method is None else self_method
        if 'start_archive_date' in kwargs and 'to' not in kwargs:
            kwargs['to'] = kwargs['start_archive_date']

        page = start_page
        while True:
            try:
                form = {'to': kwargs['to'], 'from': kwargs['start_archive_date'], 'page': page, 'mode': 'date'}
                response = await self_method(page=page, form=form, **kwargs)
                response_data = response[data]
            except Exception as e:
                raise e

            yield response_data, page
            page += 1

            if page > end_page:
                return

            if response[status] != status_ok or response[stop]:
                return

            await asyncio.sleep(random.uniform(.1, sleep_secs))

    async def get_and_save_archive(self, **kwargs):
        fn_prefix = kwargs.pop('fn_prefix')
        lottery_name = self.lottery_name

        if 'archive_date' in kwargs:
            archive_date_int = kwargs.pop('archive_date')
            # set local func var for subsequent filename formatting
            archive_date = today(archive_date_int, self.archive_filename_date_format)

            all_ = []

            async for response_data, page in self.yield_archive_page(
                    start_archive_date=today(archive_date_int),
                    **kwargs
            ):
                page_num = str(page).zfill(6)
                fn = fn_prefix.format(**locals())  # set curly braced param from str
                await save_archive(fn, response_data)

                response_data_len = len(response_data)
                all_.append({
                    'filename': fn,
                    'data_length': response_data_len,
                    'page': page,
                    'archive_date_int': archive_date_int,
                })
            return all_

        response = await self.get_archive(**kwargs)

        response_data = response['data']
        response_data_len = len(response_data)
        page = kwargs.pop('page')
        page_num = str(page).zfill(6)
        fn = fn_prefix.format(**locals())  # set curly braced param from str

        if response_data_len > 0:
            await save_archive(fn, response_data)

        return response_data_len, fn

    async def asynchronous(self, *args, **kwargs):
        start = time.time()

        maxpage = kwargs.pop('maxpage', 5)
        archive_days_ago = kwargs.pop('archive_days_ago')

        if archive_days_ago:
            futures = [
                self.get_and_save_archive(archive_date=date, start_page=1, **kwargs)
                for date in range(archive_days_ago)
            ]
        else:
            futures = [
                self.get_and_save_archive(page, **kwargs)
                for page in range(2, maxpage + 1)
            ]

        exceptions_ = []
        for i, future in enumerate(asyncio.as_completed(futures)):
            try:
                result = await future
                print(i, result)
            except Exception as e:
                print(f"Exception! {e}")
                exceptions_.append((i, e,))

        print(type(self).__name__, 'took: {:.2f} seconds'.format(time.time() - start), f' exceptions: {len(exceptions_)}')
        await self.session.close()

    # async def can_we_retrieve_lottery_data(self, min_secs_to_next_retrieve=10) -> bool:
    #     try:
    #         lottery_drawtime = await self.refresh_drawtime()
    #     except AssertionError as exc:
    #         print('Seems lottery drawtime format were changed!', exc)
    #         return False
    #
    #     if self.lottery_name not in lottery_drawtime:
    #         print(f'"{self.lottery_name}" not in {lottery_drawtime}')
    #         return False
    #
    #     lottery_remaining_seconds = lottery_drawtime[self.lottery_name]
    #
    #     print(f'Lottery "{self.lottery_name}" next draw after {lottery_remaining_seconds} secs, '
    #           f'with min secs to next retrieve: {min_secs_to_next_retrieve}')
    #
    #     if lottery_remaining_seconds <= min_secs_to_next_retrieve:
    #         return False
    #     return True

    def check_lottery_name(self, args, kwargs):
        if self.lottery_name:
            return
        if 'lottery_name' in kwargs:
            self.lottery_name = kwargs.pop('lottery_name')
            self.check_lottery_name(args, kwargs)
            return
        raise AttributeError('Not specified lottery name in "lottery_name=" parameter')

    def start(self, *args, **kwargs):
        self.check_lottery_name(args, kwargs)

        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.asynchronous(*args, **kwargs))
        finally:
            # loop.run_until_complete(asyncio.sleep(0.250))
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()


if __name__ == "__main__":
    pass

