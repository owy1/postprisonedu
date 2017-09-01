from unittest import TestCase
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
        #dprint(records)
        #dprint(curr_records)
        delids = [r['Id'] for r in curr_records['records']]

        bulk_delete(self.pp.sf,'Auto_Incarceration_Check__c',ids=delids)

        # First test - add empty DOCLocation twice. Should only be one item after update
        # both times
        #
        for i in range(2):
            self.pp.update(records,debug=False)
            auto_records = self.pp.sf.query_all("SELECT Id from Auto_Incarceration_Check__c where Contact__c='%s'" % records[0]['Id'])
            #dprint(auto_records)
            self.assertEquals(len(auto_records['records']),1)
        # self.pp.update(records,debug=True)


    def no_testupdate(self):
        records = self.pp.query(lastname='Orr', limit=1) # Return one record with lastname Orr containing all fields
        self.assertIsNotNone(records)
        self.assertEquals(records[0]['FirstName'],'Frederick Del')
        self.assertEquals(records[0]['CorrectionsAgencyNum__c'],718288)

        #debug(records)
        self.pp.update(records,debug=True)

    def no_testbigupdate(self):
        records = self.pp.query(min_level_of_service=2)
        self.assertIsNotNone(records)

        self.pp.update(records)

