import pandas as pd
import math
import simple_salesforce as sf
import datetime as dt

def bulk_load(pp, table, csv_file):
    dates = ['SystemModstamp','CreatedDate', 'LastModifiedDate', 'LastActivityDate', 'LastCURequestDate', 'LastCUUpdateDate', 'EmailBouncedDate', 'npo02__FirstCloseDate__c', 'npo02__LastCloseDate__c', 'npo02__LastMembershipDate__c', 'npo02__MembershipEndDate__c', 'npo02__MembershipJoinDate__c', 'Index_Date_Selfreported__c', 'REMOVE_Recidivism_Date__c', 'Last_Index_Date_DOCreported__c', 'Application_Service_Date__c', 'Adjusted_S_Code_Date__c', 'Adjusted_Risk_Level_Date__c']

    df = pd.read_csv(csv_file,parse_dates=dates)
    assert(pp.sandboxname)
    df = df.head(1)
    bulkl = []
    for row in df.itertuples():
        row = row._asdict()
        del row['Index']
        del row['REMOVE_Recidivism_Date__c']
        del row['No_Resource_Denial__c']
        del row['Remove_RecidivismStatus__c']
        del row['npe01__SystemIsIndividual__c']
        del row['Research_Comments_Notes__c']
        del row['HasOptedOutOfEmail']
        del row['DoNotCall']
        del row['HasOptedOutOfFax']
        del row['Id']
        row = {k:v for k,v in row.items() if not pd.isnull(v) or v == 'nan' }
        row = {k:v for k,v in row.items() if not k.startswith('np')}
        print(row)
        for c in dates:
            if row.has_key(c):
                try:
                    #row[c] = dt.datetime.strftime(row[c], '%Y-%m-%d:T%H:%M:%SZ')
                    row[c] = row[c].isoformat() + ".000+0000"
                except AttributeError:
                    row[c] = None
        print(row)
        bulkl.append(row)
    pp.sf.Contact.create(bulkl[0])
