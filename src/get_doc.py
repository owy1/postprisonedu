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

class PostPrisonSF(object):
    def __init__(self,username=None, password=None, security_token=None,sandboxname=None):
        sandbox = False
        if sandboxname is not None:
            username += "." + sandboxname
            sandbox = True
        self.sf = Salesforce(username=username, password=password, security_token=security_token,sandbox=sandbox)
        self._default_fields = ('Id','LastName','FirstName','Name','CorrectionsAgencyNum__c','DOCAgencyNumType__c',
                                'Level_of_Service_singleApp__c','Application_Level_of_Service__c','LastModifiedDate',
                                'Index_Date_Selfreported__c','LastActivityDate','Last_Index_Date_DOCreported__c','CreatedDate',
                                'Risk_Level__c','Application_Service_Date__c','Application_ERD__c' )

    def query(self,lastname=None, limit=None, fields=None, update_with_corrections=True, min_level_of_service=1):
        """
        Get contact info from PostPrison db.
        :param lastname: Lastname of contact in SF db. If None, all lastnames
        :param limit: Maximum number of objects to return. If None, no limit
        :param fields: Contact fields to return. Use '*' to return all fields
        :param update_with_corrections: Update records with incarceration info.
        :param min_level_of_service: Minimum PostPrison level of service to include
        :return: List of SF objects matching query
        """
        sf = self.sf
        self.min_level_of_service = min_level_of_service
        if fields is None:
            fields = ','.join(self._default_fields)
        elif fields == '*':
            fields = [d['name'] for d in sf.Contact.describe()['fields']]
            fields = ','.join(fields)

        sqlquery = "SELECT %s from Contact where Application_Level_of_Service__c != null" % fields
        if lastname is not None:
            sqlquery += " and LastName='%s' " % lastname
        if limit is not None:
            sqlquery += " limit %d" % limit
        log.debug("Sqlquery is %s" % sqlquery)

        records = []
        unsupportedDocTypes = set()
        bad = 0
        for record in self._filter(sf.query_all(sqlquery)['records']):
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
                    records.append(record)
                except ValueError as e:
                    log.debug("Error reading id for %s: %s" % (record.get('Name'), e.message))
                    log.debug("Bad record was %s" % json.dumps(record, indent=4))

        log.debug("Unsupported doc types=%s" % unsupportedDocTypes)
        log.info("Fail/good %d/%d" % (bad, len(records)))
        if not update_with_corrections:
            return records
        return self._get_doc_info(records)

    def _filter(self,records):
        '''
        Extra filtering that can't be done with SOQL
        :param: Input records
        :return: Filtered records
        '''
        if self.min_level_of_service is not None:
            field = 'Level_of_Service_singleApp__c'
            def filter_dict(di):
                for k,v in di.items():
                    if k == field:
                        if v is not None and v.isdigit():
                            di[k] = int(v)
                        else:
                            di[k] = None
                return di
            records = [filter_dict(di) for di in records]
            records = [di for di in records if di[field] >= self.min_level_of_service]
        return records

    def _get_doc_info(self, sfrecords):
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


def debug(ob, indent=4, sort=True, remove_null=False):
    '''
    Pretty print SalesForce objects
    :param ob: 
    :return: None
    '''
    if remove_null:
        ob = [{k:v for k,v in di.items() if v is not None} for di in ob]
    print(json.dumps(ob, indent=indent, sort_keys=sort))

if __name__ == '__main__':
    '''
    debug(pp.query(lastname='Jones',fields='*', limit=1))  # Return one record with lastname Jones containing all fields
    debug(pp.query(lastname='Chertok'))  # Return all record with lastname Chertok containing default fields
    debug(pp.query(lastname='Bride', update_with_corrections=False))  # Return all record with lastname Bride containing default fields.
                                                                      # Don't query DOC database
    
    '''
    username = os.environ.get('username')
    password = os.environ.get('password')
    security_token = os.environ.get('security_token')
    pp = PostPrisonSF(username=username, password=password, security_token=security_token, sandboxname='opheliapp')
    #debug(pp.query(lastname='Jones',limit=5))
    query = pp.query(min_level_of_service=3)
    debug(query, remove_null=True)
    print(len(query))

