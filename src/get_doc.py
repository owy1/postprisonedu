from __future__ import print_function
import requests
from bs4 import BeautifulSoup
import json
import argparse

# DOC Web site
_BaseUrl = 'http://www.doc.wa.gov/information/inmate-search/default.aspx'

# Ugly set of POST arguments required by DOC Web site
_PostArgs = '_LASTFOCUS=&__EVENTTARGET=&__EVENTARGUMENT=&__VIEWSTATE=%2FwEPDwULLTExODIwNjM0ODhkZKzRISt7X2wgEn2vPGJSCpDazTB%2F&__VIEWSTATEGENERATOR=49D7FAF8&__EVENTVALIDATION=%2FwEWAwLZm5CKDQLs0bLrBgKM54rGBtTJonjNDNMNp6w59DBLP%2F8kvVPI&Button1=Submit'

def get_doc(docid):
    """
    Request information from DOC Web site based on inmate's DOC number
    :param docid:
    :return: JSON string with inmate info (or empty JSON if no match)
    """
    payload = _PostArgs + '&TextBox1=%d' % docid
    r = requests.post(_BaseUrl, data=payload, headers={'Content-type': 'application/x-www-form-urlencoded'})
    html = BeautifulSoup(r.text, 'html.parser')
    tds = [td.text.strip().replace(':', '') for td in html.find_all('td')]
    return dict(zip(tds[::2], tds[1::2]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get DOC info on an inmate')
    parser.add_argument('docid', type=int, nargs=1, help='DOC id (for example, 118603)')
    FLAGS, unparsed = parser.parse_known_args()
    print(json.dumps(get_doc(FLAGS.docid[0])))
