import requests
import urllib3
from requests.exceptions import RequestException
try:
    from urllib.parse import urlsplit, urljoin  # Python 3
except ImportError:
    from urlparse import urlsplit, urljoin  # Python 2
from . import error_utils


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

user_agent = "Mozilla/5.0 AppleWebKit/537.36 Chrome/66.0.3359.181"


def hostname_from_url(url):
    url_parts = urlsplit(url)
    if url_parts.netloc:
        return url_parts.scheme + "://" + url_parts.netloc
    else:
        return None


def relative_url(url):
    url_parts = urlsplit(url)
    link_relative = url_parts.path
    if url_parts.query:
        link_relative += "?" + url_parts.query
    return link_relative


def internal_relative_url(url, internal_hostname):
    url_parts = urlsplit(url)

    host_without_scheme = url_parts.netloc
    if not host_without_scheme:
        return url

    url_hostname = "%s://%s" % (url_parts.scheme, url_parts.netloc)
    if internal_hostname == url_hostname:
        return url.replace(internal_hostname, "", 1)
    else:
        return False


# urljoin - make absolute URL from relative URL
# we need this, because URL-s on website are relative to base_url not url_host
# https://stackoverflow.com/questions/10893374/python-confusions-with-urljoin
# works fine with <base href="">
def make_absolute_url(base_url, url):
    return urljoin(base_url, url)


def has_valid_scheme(url, schemes):
    parts = urlsplit(url)
    return parts.scheme in schemes


def trim_url(url):
    # delete URL-s like data:image/png;base64
    if url[:4] == "data":
        return False
    else:
        return url.split("?")[0]


# check if pass URL to Chrome
# connection exception = NO
# content-type not HTML and no error = NO (is valid file)
# other (OK, HTTP error code) = YES
def check_valid_for_chrome(url, timeout):
    headers = {'user-agent': user_agent}
    try:
        r = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True, verify=False)
    except RequestException as e:
        return {
            "status": "no",
            "error_name": type(e).__name__
        }
    content_type = r.headers["Content-Type"] if "Content-Type" in r.headers else "unknown"
    not_html = not content_type.startswith("text/html")
    if not_html and r.ok:
        content_length = int(r.headers["Content-Length"]) if "Content-Length" in r.headers else None
        return {
            "status": "file",
            "content_type": content_type,
            "content_length": content_length
        }
    return {"status": "yes"}


def check_valid_200_html(url, timeout):
    headers = {'user-agent': user_agent}
    try:
        r = requests.head(url, headers=headers, timeout=timeout, allow_redirects=False, verify=False)
    except RequestException as e:
        error_utils.exit_with_message("Connection failed: %s" % type(e).__name__)
        return
    if r.is_redirect:
        msg = "Start URL %s redirects to %s" % (url, r.headers["Location"])
        msg += "\nPlease provide non-redirecting URL"
        error_utils.exit_with_message(msg)
    if not r.ok:
        http_status = r.headers["Status"] if "Status" in r.headers else r.status_code
        error_utils.exit_with_message("Start URL returned HTTP error '%s'" % http_status)
    if "Content-Type" not in r.headers or not r.headers["Content-Type"].startswith("text/html"):
        error_utils.exit_with_message("Start URL is not HTML page")
