import boto3
import json
import logging
import base64
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

logger = logging.getLogger()

def lambda_handler(event, context):
    
    print(event)
    
    for image in event['Records']:
        title = image["s3"]["object"]["key"]
    
    s3 = boto3.client('s3')
    tresponse = s3.head_object(Bucket="photobalti", Key=title)
    
    clabel = tresponse["ResponseMetadata"]["HTTPHeaders"]["x-amz-meta-customlabels"]
    
    dans = []
    
    if(clabel == "*" or clabel == ""):
        dans = []
    else:
        nlabel = clabel.split(",")
        nlabel = [x.strip(' ') for x in nlabel]
        dans = nlabel
    
    client = boto3.client('rekognition')
    pass_object = {'S3Object':{'Bucket':"photobalti",'Name': title}}
    
    response = client.detect_labels(Image = pass_object)
    
    label_ans = []
    for label in response['Labels']:
        label_ans.append(label['Name'])
        
    label_ans = label_ans + dans
    
    print(label_ans)
    
    #insert into the opensearch
    
    openSearchEndpoint = 'https://search-cloudphoto-byufvbrjtq64wz6pb3xg6rt4ue.us-east-1.es.amazonaws.com/' 
    region = 'us-east-1'
    accessID='AKIA5LRP4YP4HAYANZ4W'
    secretKey = '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'

    service = 'es'
    credentials = boto3.Session(region_name=region, aws_access_key_id=accessID, aws_secret_access_key=secretKey).get_credentials()
    awsauth = AWS4Auth(accessID, secretKey, region, service, session_token=credentials.token)

    search = OpenSearch(
        hosts = openSearchEndpoint,
        http_auth = awsauth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )
    
    try:
        es_response = search.index(
        index = 'pdata',
        body = {
            'fileID': title,
            'labels':label_ans 
        },
        refresh = True)
        print(es_response)

    except:
        print('Insert Failed OS')

    return {
        'statusCode': 200,
        'body': json.dumps('Hel')
    }
      