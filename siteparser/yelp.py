from base.parserbase import ParserBase, BlockedError
import toolbox.location as lt
import toolbox.extractor as et
from bs4 import BeautifulSoup as Bs
from urlparse import urljoin
import re
import urllib2
import config
import lib.dbclient as dc
from lib.dbclient import DbClient
import logging

class YelpParser(ParserBase):
    SITE_URL = "http://www.yelp.com/search?find_desc={keyword}&find_loc={zipcode}"
    REDIRECT_PATTERN = re.compile(r"biz_redir\?url=(?P<site_url>.*?)&")

    def __init__(self, keyword, start_zip= None, proxy_client=None):
        super(self.__class__, self).__init__(proxy_client)

        if keyword is None:
            raise SystemExit('Keyword is required for this parser.')

        self.keyword = keyword
        self.zipcode_list = lt.get_us_zipcodes_by_state()
        self.current_state = None
        self.current_city = None
        self.current_zipcode = None
        self.db = DbClient()

        if start_zip is not None:
            while not (start_zip in self.zipcode_list[0][0]):
                del self.zipcode_list[0]

            zipcode_tuple = self.zipcode_list[0]
            pos = zipcode_tuple.index(start_zip)
            zipcode_tuple[0] = zipcode_tuple[0][pos:]

    def get_key_fields(self):
        return {dc.KEY_UNIQUE: ['emails', 'yelp_url']}

    def process_batch(self):
        for zipcode_list, city, state in self.zipcode_list:
            self.current_state = state
            self.current_city = city
            for zipcode in zipcode_list:
                logging.debug("Processing zipcode<"+str(zipcode)+">, keyword<"+self.keyword+">")
                self.current_zipcode = zipcode

                next_page = self._get_url(zipcode)
                while next_page:
                    logging.debug("Started page: "+next_page)
                    for i in range(config.MAXIMUM_RETRY):
                        try:
                            [data, next_page] = self._parse_page(next_page)
                            break
                        except BlockedError:
                            if self.proxy_client is not None:
                                self.proxy_client.change_identity()
                            else:
                                raise BlockedError('Probably blocked, got a not parsable page:<' +
                                                   str(self.current_zipcode) + '> '+next_page)

                    if i == (config.MAXIMUM_RETRY - 1):
                        raise BlockedError('We are stuck, and changing proxy doesn\'t work <' +
                                           str(self.current_zipcode) + '> ')

                    yield data

    def _get_url(self, zipcode):
        return self.SITE_URL.format(keyword=self.keyword, zipcode=zipcode)

    def _get_site_url_from_redirect(self, redirect_url):
        m = re.search(self.REDIRECT_PATTERN, redirect_url)
        if m:
            return urllib2.unquote(m.group('site_url'))
        else:
            return None

    def _extract_info(self, url):
        if self.db.check_unique_key('yelp_url', url) is not None:
            logging.debug("Url parsed before, skipping: "+url)
            return None

        logging.debug("Extracting info: "+url)
        html = self._get_page(url)
        soup = Bs(html)
        name = soup.find('h1')

        try:
            if not (name['itemprop'] == 'name'):
                raise BlockedError

            name = name.string.strip() if name else None
            phone = soup.find(id='bizPhone')
            phone = phone.string.strip() if phone else None
            site = soup.find(id='bizUrl')
            site = self._get_site_url_from_redirect(site.a['href']) if site else None
        except:
            raise BlockedError('Probably blocked, got a not parsable page:<' +
                               str(self.current_zipcode) + '> '+url)

        logging.debug("Crawling site for emails: "+url)
        emails = et.find_emails_by_url(site) if site else []
        logging.debug("Crawled.")
        return {
            'name': name,
            'job': self.keyword,
            'phone': phone,
            'url': site,
            'emails': emails,
            'state': self.current_state,
            'city': self.current_city,
            'zipcode': self.current_zipcode,
            'yelp_url': url
        }

    def _parse_page(self, url):
        logging.debug("Started parsing: "+url)
        data = []
        html = self._get_page(url)
        soup = Bs(html)
        prev_next = soup.find_all(class_="prev-next")
        result_list = soup.find_all(class_='indexed-biz-name')
        del soup

        if len(prev_next) == 0:
            if len(result_list) != 0:
                next_link = None
            else:
                raise BlockedError("We are blocked by Yelp")
        else:
            next_link = prev_next[-1]
            next_link = urljoin(self.SITE_URL, next_link["href"]) if 8594 in map(ord,  next_link.string) else None

        for result in result_list:
            sub_url = urljoin(url, result.a['href'])
            for i in range(config.MAXIMUM_RETRY):
                try:
                    page_info = self._extract_info(sub_url)
                    break
                except BlockedError:
                    if self.proxy_client is not None:
                        self.proxy_client.change_identity()
                    else:
                        raise BlockedError('Probably blocked, got a not parsable page:<' +
                                           str(self.current_zipcode) + '> '+sub_url)

            if i == (config.MAXIMUM_RETRY - 1):
                raise BlockedError('We are stuck, and changing proxy doesn\'t work<' +
                                   str(self.current_zipcode) + '> ')

            if page_info is None:
                continue

            data.append(page_info)

        return [data, next_link]

