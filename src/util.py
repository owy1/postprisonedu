import pandas as pd
import math
import simple_salesforce as sf
import datetime as dt

def bulk_delete_all(pp):
    assert(pp.sandboxname)
    sf = pp.sf
    sqlquery = "Select Id from Contact"
    ids = [record['Id'] for record in sf.query_all(sqlquery)['records']]
    print(len(ids))
    ids = ['0030x000001EEk7AAG']
    for id in ids:
        pp.sf.Contact.delete(id)

# 'CorrectionsAgencyNum__c','DOCAgencyNumType__c','Level_of_Service_singleApp__c'

def bulk_load(pp, csv_file):
    assert(pp.sandboxname)
    dates = ['SystemModstamp','CreatedDate', 'LastModifiedDate', 'LastActivityDate', 'LastCURequestDate', 'LastCUUpdateDate', 'EmailBouncedDate', 'npo02__FirstCloseDate__c', 'npo02__LastCloseDate__c', 'npo02__LastMembershipDate__c', 'npo02__MembershipEndDate__c', 'npo02__MembershipJoinDate__c', 'Index_Date_Selfreported__c', 'REMOVE_Recidivism_Date__c', 'Last_Index_Date_DOCreported__c', 'Application_Service_Date__c', 'Adjusted_S_Code_Date__c', 'Adjusted_Risk_Level_Date__c']
    bad = [u'Total_Incarceration_Events__c', u'LastModifiedDate', u'IsDeleted', u'Total_Recidivisms__c', u'Application_Service_Date__c', u'Total_Applications__c', u'SystemModstamp', u'CreatedById', u'LastActivityDate', u'CreatedDate', u'Management_Only__c', u'LastModifiedById']
    bad1 = [u'LastModifiedDate', u'npe01__Lifetime_Giving_History_Amount__c', u'PhotoUrl',
         u'npo02__Formula_HouseholdMailingAddress__c', u'IsDeleted', u'Adjusted_S_Code__c',
         u'npo02__OppAmountLastYearHH__c', u'npe01__Work_Address__c', u'npe01__Home_Address__c',
         u'npe01__Last_Donation_Date__c', u'MailingAddress', u'Application_ERD__c', u'npo02__Total_Household_Gifts__c',
         u'SystemModstamp', u'npo02__Formula_HouseholdPhone__c', u'S_Code__c', u'npo02__OppAmountThisYearHH__c',
         u'LastActivityDate', u'npe01__Type_of_Account__c', u'Level_of_Service_singleApp__c',
         u'npe01__Organization_Type__c', u'Application_Level_of_Service__c', u'Name', u'CreatedById', u'Risk_Level__c',
         u'MasterRecordId', u'Total_Incarceration_Events__c', u'IsEmailBounced', u'npe01__Other_Address__c',
         u'Total_Recidivisms__c', u'LastViewedDate', u'Total_Applications__c', u'CreatedDate', u'OtherAddress',
         u'Management_Only__c', u'Adjusted_Risk_Level_Date__c', u'LastReferencedDate', u'Application_Service_Date__c',
         u'Contacts__c', u'LastCUUpdateDate', u'Adjusted_S_Code_Date__c', u'Last_Index_Date_DOCreported__c',
         u'Adjusted_Risk_Level__c', u'LastCURequestDate', u'LastModifiedById', u'npo02__LastCloseDateHH__c',
         u'JigsawContactId']
    df = pd.read_csv(csv_file,parse_dates=dates)
    for b in bad:
        del df[b]

    sf = pp.sf
    fields = [d['name'] for d in sf.Contact.describe()['fields']]
    fields = ','.join(fields)
    sqlquery = "Select %s from Contact limit 10" % fields
    records = sf.query_all(sqlquery)['records']
    for r in records[:1]:
        print(r['Level_of_Service_singleApp__c'])
        id = r['Id']
        del r['Id']
        for b in bad1: del r[b]
        r['Level_of_Service_singleApp__c'] = None
        sf.Contact.update(id,r)
        raise Exception

    # df = df.head(2)
    # bulkl = []
    # for row in df.itertuples():
    #     row = row._asdict()
    #     del row['Index']
    #     del row['REMOVE_Recidivism_Date__c']
    #     del row['No_Resource_Denial__c']
    #     del row['Remove_RecidivismStatus__c']
    #     del row['npe01__SystemIsIndividual__c']
    #     del row['Research_Comments_Notes__c']
    #     del row['HasOptedOutOfEmail']
    #     del row['DoNotCall']
    #     del row['HasOptedOutOfFax']
    #     del row['Id']
    #
    #     del row['OwnerId']
    #     del row['AccountId']
    #     row = {k:v for k,v in row.items() if not pd.isnull(v) or v == 'nan' }
    #     row = {k:v for k,v in row.items() if not k.startswith('np')}
    #     for c in dates:
    #         if row.has_key(c):
    #             try:
    #                 #row[c] = dt.datetime.strftime(row[c], '%Y-%m-%d:T%H:%M:%SZ')
    #                 row[c] = row[c].isoformat() + ".000+0000"
    #             except AttributeError:
    #                 row[c] = None
    #     bulkl.append(row)
    #print(bulkl[0])
    #pp.sf.Contact.create(bulkl[0])
