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
log.basicConfig(level=log.DEBUG)
from collections import OrderedDict
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
    session = requests.Session()
    r = session.get(_BaseUrl)
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
        r = session.post(_BaseUrl,data=payload,headers={'Content-type':'application/x-www-form-urlencoded'})
        soup = BeautifulSoup(r.text,'html.parser')
        tds = [td.text.strip().replace(':','') for td in soup.find_all('td')]
        docinfo = dict(zip(tds[:8:2],tds[1:9:2]))
        record['DOCLocation'] = docinfo.get('Location')
        record['DOCName'] = docinfo.get('Offender Name')
        info.append(record)
    return info

def get_sf_by_id(id):
    return sf.Contact.get(id)

def get_sf_ids(lastname=None, limit=None):
    """
    Get contact info from PostPrison db.
    :param lastname: Lastname of contact in SF db. If None, all lastnames
    :param limit: Maximum number of objects to return. If None, no limit
    :return: List of SF objects matching query
    """
    sqlquery = "SELECT Id,LastName,FirstName,Name,CorrectionsAgencyNum__c,DOCAgencyNumType__c,LastActivityDate from Contact "
    if lastname is not None:
        sqlquery += " where LastName='%s' " % lastname
    if limit is not None:
        sqlquery += " limit %d" % limit

    docids = []
    unsupportedDocTypes = set()
    bad = 0
    for record in sf.query_all(sqlquery)['records']:
        #debug(record)
        docid = record.get('CorrectionsAgencyNum__c')
        if docid is not None:
            try:
                agencyNum = record['DOCAgencyNumType__c']
                if agencyNum is None or not agencyNum.startswith('WA DOC'):
                    if agencyNum is not None:
                        bad += 1
                        unsupportedDocTypes.add(record['DOCAgencyNumType__c'])
                    raise ValueError("Not a DOC id")
                record['CorrectionsAgencyNum__c'] = int(docid)
                del record['attributes']
                docids.append(record)
            except ValueError as e:
                log.debug("Error reading id for %s: %s" % (record.get('Name'),e.message))
                log.debug("Bad record was %s" % json.dumps(record,indent=4))

    log.debug("Unsupported doc types=%s" % unsupportedDocTypes)
    log.info("Fail/good %d/%d" % (bad,len(docids)))
    return docids

if __name__ == '__main__':
    sf = get_login()
    #get_sf_ids()
    debug(get_doc_info(get_sf_ids(limit=100)))
    #debug(get_doc_info(get_sf_ids(lastname='Jones',limit=10)))
    #debug(get_doc_info(get_sf_ids()))

    # Roseen Redstar
    #d = get_sf_by_id("003i000000hFVF8AAO")

    #d = get_doc_info(get_sf_ids(lastname='Bride'))
    #debug(d)
    #d = get_sf_by_id('003i000004gnLL7AAM')

    # d = get_doc_info(get_sf_ids(lastname='Chertok'))
    # debug(d)
    #d = get_sf_by_id('003i000000gDakgAAC')

    # for k in sorted(d.keys()):
    #     v = d[k]
    #     if v is not None:
    #         print(k,':',v)


