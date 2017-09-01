from unittest import TestCase
import unittest
import os
from get_doc import PostPrisonSF,dprint
from util import bulk_delete


class TestPostPrisonSF(TestCase):

    def setUp(self):
        username = os.environ.get('username')
        password = os.environ.get('password')
        security_token = os.environ.get('security_token')
        self.assertIsNotNone(username)
        self.assertIsNotNone(password)
        self.assertIsNotNone(security_token)

        self.pp = PostPrisonSF(username=username, password=password, security_token=security_token)

    def testupdate(self):
        records = self.pp.query(lastname='Test', limit=1)
        self.assertIsNotNone(records)
        self.assertEquals(records[0]['FirstName'],'Test')
        self.assertEquals(records[0]['CorrectionsAgencyNum__c'],0)

        sqlquery = 'SELECT Id from Auto_Incarceration_Check__c'
        sqlquery += " where Contact__c='%s'"% records[0]['Id']
        curr_records = self.pp.sf.query_all(sqlquery)
        delids = [r['Id'] for r in curr_records['records']]

        bulk_delete(self.pp.sf,'Auto_Incarceration_Check__c',ids=delids)

        # First test - add empty DOCLocation twice. Should only be one item after update
        # both times
        #
        for i in range(2):
            self.pp.update(records,debug=False)
            auto_records = self.pp.sf.query_all("SELECT Id from Auto_Incarceration_Check__c where Contact__c='%s'" % records[0]['Id'])
            self.assertEquals(len(auto_records['records']),1)



        # Add a new record. Should now be two records
        records[0]['DOCLocation'] = 'Fake facility'

        for i in range(2):
            self.pp.update(records, debug=False, force_records=True)
            auto_records = self.pp.sf.query_all(
                "SELECT Id from Auto_Incarceration_Check__c where Contact__c='%s'" % records[0]['Id'])
            self.assertEquals(len(auto_records['records']), 2)
            query = "SELECT DOCLocation__c from Contact where Id='%s'" % records[0]['Id']
            contact_records = self.pp.sf.query_all(query)
            self.assertEquals(contact_records['records'][0]['DOCLocation__c'],'Fake facility')

    @unittest.skip("Skipping big slow test")
    def testbigupdate(self):
        records = self.pp.query(min_level_of_service=2)
        self.assertIsNotNone(records)

        self.pp.update(records)

