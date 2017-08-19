from __future__ import print_function
import requests
import os
from bs4 import BeautifulSoup
import json
import argparse
import urllib
from six.moves.urllib.parse import quote
from simple_salesforce import Salesforce
import pytz
import datetime
import json

# DOC Web site
_BaseUrl='http://www.doc.wa.gov/information/inmate-search/default.aspx'

# Ugly set of POST arguments required by DOC Web site
_PostArgs='__VIEWSTATE=%s&__VIEWSTATEGENERATOR=%s&__EVENTVALIDATION=%s&Button1=Submit&TextBox1=%s'


def get_login():
    """."""
    username = os.environ.get('username')
    password = os.environ.get('password')
    security_token = os.environ.get('security_token')
    sf = Salesforce(username=username, password=password, security_token=security_token)
    return sf

def get_doc(docid):
    '''
    Request information from DOC Web site based on inmate's DOC number
    :param docid:
    :return: JSON string with inmate info (or empty JSON if no match)
    '''
    # First request to get ASP.net state info
    r = requests.get(_BaseUrl)
    soup = BeautifulSoup(r.text,'html.parser')
    viewstate = quote(soup.select("#__VIEWSTATE")[0]['value'],safe='')
    eventvalidation = quote(soup.select("#__EVENTVALIDATION")[0]['value'],safe='')
    vsg = quote(soup.select("#__VIEWSTATEGENERATOR")[0]['value'],safe='')
    payload = _PostArgs % (viewstate,vsg,eventvalidation,docid)

    # Now post and retrieve results
    r = requests.post(_BaseUrl,data=payload,headers={'Content-type':'application/x-www-form-urlencoded'})
    soup = BeautifulSoup(r.text,'html.parser')
    tds = [td.text.strip().replace(':','') for td in soup.find_all('td')]
    rval = [dict(zip(tds[i:i+8:2],tds[i+1:i+9:2])) for i in range(len(tds)) if i%8 == 0]
    return rval

def debug(o,indent=4):
    '''
    Pretty print SalesForce objects
    :param o: 
    :return: None
    '''
    print(json.dumps(o,indent=indent))


def get_sf_ids():
    #debug(sf.Contact.describe())
    #raise Exception
    docids = []
    for record in sf.query_all("SELECT LastName,FirstName,Name,CorrectionsAgencyNum__c from Contact where LastName='Jones' limit 1")['records']:
        debug(record)
        docids.append(int(record['CorrectionsAgencyNum__c']))
    return docids

if __name__ == '__main__':
    sf = get_login()
    temp = get_sf_ids()
    debug(get_doc(temp[0]))
   # parser = argparse.ArgumentParser(description='Get DOC info on an inmate')
   # parser.add_argument('docid', type=str, nargs=1, help='DOC id or name(for example, 118603)')
   # FLAGS, unparsed = parser.parse_known_args()
   # print(json.dumps(get_doc(FLAGS.docid[0])))
