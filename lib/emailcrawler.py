import config
from bs4 import BeautifulSoup
from toolbox.url import url_open
import urlparse
import re


class EmailCrawler:
    MAIL_REGEX = re.compile(r'[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}')
    ROBOTS_SITEMAP = re.compile(r'Sitemap:[ ]*(?P<sitemap_url>[^ ]*)')

    def __init__(self, url):
        self.url = url
        self.urls_to_crawl = []
        self.urls_added = set()
        self.max_depth = config.EMAIL_EXTRACTOR_DEPTH
        self.emails = set()
        self.urls_crawled = 0

    def run(self):
        self._crawl_sitemap()

        if len(self.urls_to_crawl) == 0:
            self.urls_to_crawl.append((self.url, 1))

        while (self.urls_crawled <= config.EMAIL_EXTRACTOR_MAX_URLS) and len(self.urls_to_crawl):
            current_url, current_depth = self.urls_to_crawl[0]
            self.urls_to_crawl = self.urls_to_crawl[1:]
            emails = self._crawl_page(current_url, current_depth)

            for email in emails:
                email = email.lower()
                self.emails.add(email)

        return list(self.emails)

    def _crawl_page(self, url, depth=1, recursive=True):
        data = url_open(url, True)

        if data is None:
            return []

        if recursive and (depth < self.max_depth):
            soup = BeautifulSoup(data)
            links = soup.find_all('a')
            for link in links:
                try:
                    new_loc = urlparse.urlparse(link['href']).netloc
                    if new_loc and not (urlparse(url).netloc ==new_loc):
                        continue

                    href = urlparse.urljoin(url, link['href'])
                except:
                    continue

                if not (href in self.urls_added):
                    self.urls_to_crawl.append((href, depth+1))
                    self.urls_added.add(href)

        emails = re.findall(self.MAIL_REGEX, data)
        self.urls_crawled += 1
        return emails

    def _crawl_sitemap(self):
        links = self._get_sitemap()

        for link in links:
            if link in self.urls_added:
                continue

            self.urls_added.add(link)
            self.urls_to_crawl.append((link, 1))

    def _get_sitemap(self):
        sitemap_url = self._get_sitemap_url()
        links = []
        try:
            response = url_open(sitemap_url)
            soup = BeautifulSoup(response)
            links = map(lambda x: x.string, soup.find_all('loc'))
        finally:
            return links

    def _get_sitemap_url(self):
        robots_url = urlparse.urljoin(self.url, 'robots.txt')
        path = 'sitemap.xml'

        try:
            response = url_open(robots_url)
            m = re.search(self.ROBOTS_SITEMAP, response)
            path = m.groups()[0]
        finally:
            return urlparse.urljoin(self.url, path)



