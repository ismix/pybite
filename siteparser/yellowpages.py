from base.parserbase import ParserBase, BlockedError
import lib.dbclient as dc
from bs4 import BeautifulSoup as Bs
import toolbox.extractor as et
import logging
import config


class YellowpagesParser(ParserBase):
    SITE_URL = "http://www.yellowpages.com/{state}/{keyword}?page={page_num}"

    def __init__(self, params=None, proxy_client=None):
        super(self.__class__, self).__init__(proxy_client)

        if params is None or 'keyword' not in params:
            raise SystemExit('keyword is required for this parser.')
        elif 'state' not in params:
            raise SystemExit('state is required for this parser.')

        self.keyword = params['keyword']
        self.state = params['state']
        self.page_num = int(params['page_num']) if 'page_num' in params else 1
        self.db = dc.DbClient()

    def get_key_fields(self):
        return {dc.KEY_UNIQUE: ['emails', 'url']}

    def process_batch(self):
        finished = False

        while True:
            for i in range(config.MAXIMUM_RETRY):
                try:
                    data = self._get_listings()
                except BlockedError as ex:
                    if self.proxy_client is not None:
                        logging.debug('Got a blocked error, change id and try again: '+ex.message)
                        self.proxy_client.change_identity()
                        continue
                    else:
                        raise BlockedError('Got a blocked error: '+ex.message)

                self.page_num += 1

                if not data:
                    finished = True
                    break

                yield data

            if finished:
                break

            if i == (config.MAXIMUM_RETRY - 1):
                raise BlockedError('We are stuck, and changing proxy doesn\'t work, url: '+self.current_url)

        logging.debug('Parse for keyword: '+self.keyword+' and state: '+self.state+' ended gracefully.')

    def _get_listings(self):
        self._set_current_url()
        logging.debug('Started getting listings from url: '+self.current_url)
        html = self._get_page(self.current_url)
        soup = Bs(html)
        data = []

        if soup.find(class_='error-page'):
            logging.debug('Hit a dead-end at url: '+self.current_url)
            return False

        listings = soup.find_all(class_='listing-content')

        if listings is None or not len(listings):
            raise BlockedError('No error-page, no listings. Blocked maybe? at url: '+self.current_url)

        logging.debug('Got listings successfully, getting details at url: '+self.current_url)
        for listing in listings:
            data_part = self._get_listing_detail(listing)
            if data_part is not None:
                data.append(data_part)

        return data

    def _get_listing_detail(self, listing):
        try:
            name = listing.h3.a.string
            category = listing.find(class_='business-categories')
            category = map(lambda a: a.string.strip(), category.find_all('a')) if category else None
            url = listing.find(class_='track-visit-website')
            url = url['href'] if url else None

            if self.db.check_unique_key('url', url) is not None:
                logging.debug("Url parsed before, skipping: "+url)
                return None

            phone = listing.find(class_='business-phone')
            phone = phone.string if phone else None

            if url is not None:
                logging.debug('Crawling url for emails: '+url)
                emails = et.find_emails_by_url(url)
            else:
                emails = []
        except Exception as ex:
            raise BlockedError("Probably blocked, url: "+self.current_url+", msg: "+ex.message)

        data = {
            'name': name,
            'categories': category,
            'url': url,
            'phone': phone,
            'state': self.state.upper(),
            'emails': emails
        }

        return data

    def _set_current_url(self):
        self.current_url = self.SITE_URL.format(state=self.state, keyword=self.keyword, page_num=str(self.page_num))

