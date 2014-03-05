import urllib2
import config


def url_open(url, html_only=False):
    request = urllib2.Request(url)
    request.add_header('User-Agent', 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.4) Gecko/20091030 Gentoo Firefox/3.5.4')
    opener = urllib2.build_opener()
    try:
        response = opener.open(request, timeout=config.URLLIB_TIMEOUT)

        if html_only and not ('text/html' in response.info().getheader('Content-Type')):
            return None

        return response.read()
    except:
        return None
