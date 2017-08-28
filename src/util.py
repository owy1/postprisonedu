import pandas as pd
import os
from get_doc import PostPrisonSF

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

def bulk_load(pp, csv_file,delete=False):
    dates = ["Index_Date_Selfreported__c","Last_Index_Date_DOCreported__c",'Application_ERD__c', 'Birthdate','SystemModstamp','CreatedDate', 'LastModifiedDate', 'LastActivityDate', 'LastCURequestDate', 'LastCUUpdateDate', 'EmailBouncedDate', 'npo02__FirstCloseDate__c', 'npo02__LastCloseDate__c', 'npo02__LastMembershipDate__c', 'npo02__MembershipEndDate__c', 'npo02__MembershipJoinDate__c', 'Index_Date_Selfreported__c', 'REMOVE_Recidivism_Date__c', 'Last_Index_Date_DOCreported__c', 'Application_Service_Date__c', 'Adjusted_S_Code_Date__c', 'Adjusted_Risk_Level_Date__c']
    bad = [u'LastModifiedDate', u'CreatedById', u'MasterRecordId', u'IsDeleted', u'CreatedDate', u'LastCUUpdateDate', u'LastCURequestDate', u'SystemModstamp', u'LastActivityDate',u'LastModifiedById', u'JigsawContactId']
    df = pd.read_csv(csv_file,parse_dates=dates)

    df['Level_of_Service_singleApp__c'] = 0
    df.loc[df.Total_Applications__c == 1,'Level_of_Service_singleApp__c'] = df[df.Total_Applications__c == 1]['LOSAggregate__c']
    df.loc[df.Level_of_Service_singleApp__c.isnull()] = 0
    df['Level_of_Service_singleApp__c'] = df['Level_of_Service_singleApp__c'].astype(int)

    sf = pp.sf
    fields = [d['name'] for d in sf.Contact.describe()['fields']]
    fields = list(set(fields).intersection(df.columns))
    df = df[fields]

    sqlquery = "Select Id from Contact"
    records = sf.query_all(sqlquery)['records']
    delids = [{'Id':r['Id']} for r in records]
    sf.bulk.Contact.delete(delids)

    for b in bad:
        del df[b]
    for c in df.columns:
        if c.find('Id') >= 0:
            del df[c]
    bulk = []
    flush_at = 10
    for i,row in enumerate(df.itertuples()):
        row = row._asdict()
        del row['Index']
        row = {k:v for k,v in row.items() if pd.notnull(v) and v != 'nan' and v is not None}
        for c in dates:
            if row.has_key(c):
                try:
                    row[c] = row[c].isoformat() + ".000+0000"
                except AttributeError:
                    row[c] = None
        bulk.append(row)
        if i > 0 and i % flush_at == 0:
            print('Count = %d' % i)
            try:
                pp.sf.bulk.Contact.insert(bulk)
            except:
                print("Error**********")
                print(bulk)
            bulk = []
    if len(bulk) > 0: pp.sf.bulk.Contact.insert(bulk)

if __name__ == '__main__':
    username = os.environ.get('username')
    password = os.environ.get('password')
    security_token = os.environ.get('security_token')
    assert(username.startswith('sir'))
    pp = PostPrisonSF(username=username, password=password, security_token=security_token)
    bulk_load(pp, '../data/dump/Contact.csv', delete=True)

