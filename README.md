# postprisonedu
PuPPy project with Post-Prison Education Program in-progress

1) create postprisonedu Salesforce Enterprise, github, slack accounts for development.
2) create a salesforce sandbox for development
3) use beautifulsoup to scrape html pages:
    'http://www.doc.wa.gov/information/inmate-search/default.aspx'
    'https://www.bop.gov/inmateloc/'
4) use six.moves.urllib for python 2 and 3 compatibility

Required changes to PostPrison SF:

1) Add Auto_Incarceration_Check__c as child of Contact with following fields:
   DOCAgencyNumType(text)
   DOCLocation(text)
  
   History should be enabled on Auto_Incarceration_Check__c
2) Add DOCLocation(text) to Contact
