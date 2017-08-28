from unittest import TestCase
import os
from get_doc import PostPrisonSF


class TestPostPrisonSF(TestCase):

    def setUp(self):
        username = os.environ.get('username')
        password = os.environ.get('password')
        security_token = os.environ.get('security_token')
        self.assertIsNotNone(username)
        self.assertIsNotNone(password)
        self.assertIsNotNone(security_token)

        self.pp = PostPrisonSF(username=username, password=password, security_token=security_token)

    def testpp(self):
        records = self.pp.query(lastname='Orr', limit=10) # Return one record with lastname Jones containing all fields
        self.assertIsNotNone(records)
        self.assertEquals(records[0]['FirstName'],'Frederick Del')
        self.assertEquals(records[0]['CorrectionsAgencyNum__c'],718288)

