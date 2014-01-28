from lib.emailcrawler import EmailCrawler
import whois
import re
import urlparse

"""
We need major email domain list to filter emails that we get, so that we will not collect unrelated email addresses
like domain proxies.
"""
MAJOR_DOMAIN_LIST = {'yahoo', 'gmail', 'hotmail', 'googlemail', 'gmx', 'mail', 'web', 'live', 'aol',
                     'yandex', 'me', 'msn', 'comcast', 'hushmail'}

"""
A regular expression to extract domain part of email.
"""
EMAIL_DOMAIN_REGEX = re.compile(r'@(?P<domain>\w+?)\.')


def find_emails_by_url(url):
    """
    The main function to be called. It first parses the site to find emails. If that is unsuccessful, it will try to
    extract email address from whois record. It filters all emails by domain to sanity check before returning.

    @type url: string
    @param url: A site address string

    @rtype: list
    @return: List of emails collected for url
    """
    url = url.lower()

    if urlparse.urlparse(url).scheme == '':
        url = 'http://'+url

    emails = find_emails_in_page(url)
    if len(emails) == 0:
        raw_emails = find_emails_by_dns(url)
        emails = filter_emails_by_domain(raw_emails, url)

    return emails


def find_emails_in_page(url):
    """
    Spawns an EmailCrawler object to parse site and return emails found on the page.

    @type   url: string
    @param  url: A site address string

    @rtype: list
    @return: List of emails collected for url
    """
    emails = EmailCrawler(url).run()
    return emails


def find_emails_by_dns(url):
    """
    Extracts whois registrant email information and returns it. You should be careful when you are using it since you
    may get private registration proxy emails. Try to use it filter_emails_by_domain function.

    @type   url: string
    @param  url: A site address string

    @rtype: list
    @return: List of emails from whois registrant record for url
    """
    try:
        wh = whois.whois(url)
        email = re.search(r'Registrant Email: (?P<email>.*)', wh.text).group(1)
        return [email.strip()]
    except:
        return []


def filter_emails_by_domain(emails, url=''):
    """
    Filter email addresses using major domains list and site url, and only return the ones with the matching domain.

    @type   emails: list
    @param  emails: A list of emails to be filtered by domain
    @type   url: string
    @param  url: A site address to search domain in

    @rtype: list
    @return: List of filtered emails
    """
    filtered_emails = []

    for email in emails:
        domain_match = re.search(EMAIL_DOMAIN_REGEX, email)

        if not domain_match:
            continue

        domain = domain_match.group('domain').lower()

        if (domain in MAJOR_DOMAIN_LIST) or (domain in url):
            filtered_emails.append(email)

    return filtered_emails
