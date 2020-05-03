class StolotoArchiveUrls(object):
    """Url generator for Stoloto archive"""
    lottery_name = ''

    MAIN_URL = 'https://www.stoloto.ru'
    MAIN_ARCHIVE_POSTFIX = 'archive'
    ARCHIVE_PREFIX = 'draw-results'
    ARCHIVE_POSTFIX = 'load'

    def __init__(self, lottery_name=None):
        if lottery_name:
            self.lottery_name = lottery_name

    def check(self):
        assert self.lottery_name != '', 'You need specify lottery name'
        assert self.MAIN_URL != '', 'self.MAIN_URL must not be an empty string'

    @property
    def main_archive_page_url(self):
        self.check()
        return f'{self.MAIN_URL}/{self.lottery_name}/{self.MAIN_ARCHIVE_POSTFIX}'

    @property
    def archive_page_url(self):
        self.check()
        # 'https://www.stoloto.ru/draw-results/rapido2/load'
        return f'{self.MAIN_URL}/{self.ARCHIVE_PREFIX}/{self.lottery_name}/{self.ARCHIVE_POSTFIX}'

    @property
    def fastgames_draw_time_url(self):
        return f'{self.MAIN_URL}/fastgames/info/all-game-draw-time'
