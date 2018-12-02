# Domain blacklist

**This feature is enabled by default.**

Domain lists are used in two places:
1. `Resource -> External` report to check if website do not download any data (for example malicious JavaScript code) from malware domain.
2. `Links` report to check if there are no links to malware domains.

## Auto update

By default fresh lists are downloaded every 24 hours and you can change this or disable auto update.

Current lists are downloaded from URL listed here https://raw.githubusercontent.com/rafal-qa/page-walker/master/lib/pagewalker/domain_lists.json

## Custom domains list

It is possible to provide custom domains list.
1. Disable auto update.
2. Put custom list (one domain per line) in `config/domain_blacklist/current_list.txt`

## Additional checks

If you get information about blacklisted domain, it is worth checking with a more specialized tool:
* https://sitecheck.sucuri.net
* https://transparencyreport.google.com/safe-browsing/search
