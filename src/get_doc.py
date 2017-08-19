from __future__ import print_function
import requests
import os
from bs4 import BeautifulSoup
import json
import argparse
from six.moves.urllib.parse import quote
from simple_salesforce import Salesforce
import json
import logging as log

# DOC Web site
_BaseUrl='http://www.doc.wa.gov/information/inmate-search/default.aspx'

# Ugly set of POST arguments required by DOC Web site
_PostArgs='__VIEWSTATE=%s&__VIEWSTATEGENERATOR=%s&__EVENTVALIDATION=%s&Button1=Submit&TextBox1=%s'

def get_login():
    """
    Get a handle to a SalesForce object after authentication
    :return: SalesForce object
    """
    username = os.environ.get('username')
    password = os.environ.get('password')
    security_token = os.environ.get('security_token')
    sf = Salesforce(username=username, password=password, security_token=security_token)
    return sf

def debug(o,indent=4):
    '''
    Pretty print SalesForce objects
    :param o: 
    :return: None
    '''
    print(json.dumps(o,indent=indent))

def get_doc_info(sfrecords):
    '''
    Request information from DOC Web site based on inmate's DOC number obtained from SalesForce
    and add to SalesForce record. New fields are DOCLocation (which institution the inmate is 
    incarcerated in and DOCName, the name of the inmate as registered by the DOC
    :param sfrecords:
    :return: JSON string with inmate info (or empty JSON if no match)
    '''
    # First request to get ASP.net state info
    r = requests.get(_BaseUrl)
    soup = BeautifulSoup(r.text,'html.parser')
    viewstate = quote(soup.select("#__VIEWSTATE")[0]['value'],safe='')
    eventvalidation = quote(soup.select("#__EVENTVALIDATION")[0]['value'],safe='')
    vsg = quote(soup.select("#__VIEWSTATEGENERATOR")[0]['value'],safe='')

    # Now post and retrieve results
    info = []
    for record in sfrecords:
        docid = record['CorrectionsAgencyNum__c']
        record['DOCLocation'] = None
        if docid is None:
            log.warn("No DOC id available for %s in SalesForce Contact info" % record.get('Name'))
            continue
        payload = _PostArgs % (viewstate, vsg, eventvalidation, docid)
        r = requests.post(_BaseUrl,data=payload,headers={'Content-type':'application/x-www-form-urlencoded'})
        soup = BeautifulSoup(r.text,'html.parser')
        tds = [td.text.strip().replace(':','') for td in soup.find_all('td')]
        docinfo = dict(zip(tds[:8:2],tds[1:9:2]))
        record['DOCLocation'] = docinfo.get('Location')
        record['DOCName'] = docinfo.get('Offender Name')
        info.append(record)
    return info

def get_sf_ids(lastname=None, limit=None):
    """
    Get contact info from PostPrison db.
    :param lastname: Lastname of contact in SF db. If None, all lastnames
    :param limit: Maximum number of objects to return. If None, no limit
    :return: List of SF objects matching query
    """
    sqlquery = "SELECT Id,LastName,FirstName,Name,CorrectionsAgencyNum__c,LastActivityDate from Contact "
    if lastname is not None:
        sqlquery += " where LastName='%s' " % lastname
    if limit is not None:
        sqlquery += " limit %d" % limit

    docids = []
    for record in sf.query_all(sqlquery)['records']:
        docid = record.get('CorrectionsAgencyNum__c')
        if docid is not None:
            record['CorrectionsAgencyNum__c'] = int(docid)
        del record['attributes']
        docids.append(record)
    return docids

if __name__ == '__main__':
    sf = get_login()
    debug(get_doc_info(get_sf_ids(lastname='Jones', limit=5)))
