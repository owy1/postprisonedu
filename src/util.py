import pandas as pd
import os
from get_doc import PostPrisonSF,debug

def bulk_load_contact(pp, csv_file,delete=False):
    dates = ["Index_Date_Selfreported__c","Last_Index_Date_DOCreported__c",'Application_ERD__c', 'Birthdate','SystemModstamp','CreatedDate', 'LastModifiedDate', 'LastActivityDate', 'LastCURequestDate', 'LastCUUpdateDate', 'EmailBouncedDate', 'npo02__FirstCloseDate__c', 'npo02__LastCloseDate__c', 'npo02__LastMembershipDate__c', 'npo02__MembershipEndDate__c', 'npo02__MembershipJoinDate__c', 'Index_Date_Selfreported__c', 'REMOVE_Recidivism_Date__c', 'Last_Index_Date_DOCreported__c', 'Application_Service_Date__c', 'Adjusted_S_Code_Date__c', 'Adjusted_Risk_Level_Date__c']
    bad = [u'LastModifiedDate', u'CreatedById', u'MasterRecordId', u'IsDeleted', u'CreatedDate', u'LastCUUpdateDate', u'LastCURequestDate', u'SystemModstamp', u'LastActivityDate',u'LastModifiedById', u'JigsawContactId']
    df = pd.read_csv(csv_file)

    df['Level_of_Service_singleApp__c'] = 0
    df.loc[df.Total_Applications__c == 1,'Level_of_Service_singleApp__c'] = df[df.Total_Applications__c == 1]['LOSAggregate__c']
    df.loc[df.Level_of_Service_singleApp__c.isnull()] = 0
    df['Level_of_Service_singleApp__c'] = df['Level_of_Service_singleApp__c'].astype(int)

    sf = pp.sf
    fields = [d['name'] for d in sf.Contact.describe()['fields']]
    fields = list(set(fields).intersection(df.columns))
    df = df[fields]

    if delete:
        bulk_delete(sf,'Contact')

    for b in bad:
        del df[b]
    for c in df.columns:
        if c.find('Id') >= 0:
            del df[c]
    for c in dates:
        if c in df.columns:
            df.loc[df[c] == 0, c] = pd.NaT
            df[c] = pd.to_datetime(df[c],errors='coerce')
            df[c] = df[c].dt.strftime("%Y-%m-%d")

    bulk = []
    flush_at = 10
    for i,row in enumerate(df.itertuples()):
        row = row._asdict()
        del row['Index']
        row = {k:v for k,v in row.items() if pd.notnull(v) and v != 'nan' and v != 'NaT' and v is not None}
        bulk.append(row)
        if i > 0 and i % flush_at == 0:
            print('Count = %d' % i)
            try:
                pp.sf.bulk.Contact.insert(bulk)
            except:
                print("Failed with bulk payload ",bulk)
                print("Continuing...")
            bulk = []
    if len(bulk) > 0: pp.sf.bulk.Contact.insert(bulk)


def bulk_delete(sf,table):
    sqlquery = "Select Id from %s" % table
    records = sf.query_all(sqlquery)['records']
    delids = [{'Id': r['Id']} for r in records]
    if len(delids) > 0: sf.bulk[table].delete(delids)


def bulk_retrieve_metadata(pp,objects,output_dir):
    for o in objects:
        debug(pp.describe(o))


if __name__ == '__main__':
    # username = os.environ.get('prodsf_username')
    # password = os.environ.get('prodsf_password')
    # security_token = os.environ.get('prodsf_security_token')
    username = os.environ.get('username')
    password = os.environ.get('password')
    security_token = os.environ.get('security_token')
    pp = PostPrisonSF(username=username, password=password, security_token=security_token)
    bulk_retrieve_metadata(pp, ['Auto_Incarceration_Check__c'],'/tmp')

    # bulk_retrieve_metadata(pp, ['Contact'],'/tmp')
    # username = os.environ.get('username')
    # password = os.environ.get('password')
    # security_token = os.environ.get('security_token')
    # assert(username.startswith('sir'))
    # pp = PostPrisonSF(username=username, password=password, security_token=security_token)
    # bulk_load(pp, '../data/dump/Contact.csv', delete=True)

