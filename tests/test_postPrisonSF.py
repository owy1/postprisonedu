from unittest import TestCase
import os
from get_doc import PostPrisonSF,debug
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

