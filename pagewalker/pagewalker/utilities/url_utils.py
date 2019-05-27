from urllib.parse import urlsplit, urljoin


def hostname_from_url(url):
    url_parts = urlsplit(url)
    if url_parts.netloc:
        return url_parts.scheme + "://" + url_parts.netloc
    else:
        return None


# Link format: //example.com
def prepend_missing_scheme(url, base_url):
    url_parts = urlsplit(url)
    if url_parts.netloc and not url_parts.scheme:
        return urlsplit(base_url).scheme + ":" + url
    else:
        return url


def relative_url(url):
    url_parts = urlsplit(url)
    link_relative = url_parts.path
    if url_parts.query:
        link_relative += "?" + url_parts.query
    if not link_relative:
        link_relative = "/"
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
    return url.split("?")[0]


def all_level_subdomains(url):
    if not url:
        return []
    host = urlsplit(url).netloc
    if not host:
        return []
    subdomains = []
    parts = host.split(".")
    while len(parts) > 1:
        subdomains.append(".".join(parts))
        parts.pop(0)
    return subdomains
