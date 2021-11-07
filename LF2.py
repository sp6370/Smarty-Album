import json
import boto3
from requests_aws4auth import AWS4Auth
from opensearchpy import OpenSearch, RequestsHttpConnection
import logging
import random

logger = logging.getLogger()

def search(label):
    #OpenSearch Config
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
    
    query_keyword = label

    query = {
        'size': 20,
        'query': {
            'multi_match': {
            'query': query_keyword,
            'fields': ['labels']
            }
            }
        }
    
    response = search.search(
        body = query,
        index = 'pdata'
        )
    
    rlist = response['hits']['hits']
    
    ans = []

    if(len(rlist)==0):
        return ans

    for item in rlist:
        tmp = item['_source']['fileID']
        ans.append(tmp)
    
    return ans

def lambda_handler(event, context):

    # Call to lex to get the key words
    botClient = boto3.client('lex-runtime')
    userID = 'test'
    botName = "photoSearcher"
    botAlias = "bot_bot"
    
    #connect to frontend
    print(event)
    rawUserInput = event.get('queryStringParameters').get('q')
    # userInput = rawUserInput[0].get("unstructured").get('text')
    print('This is the message:', rawUserInput)
    
    # userInput = "show tree"
    botResponse = botClient.post_text(
        botName = botName,
        botAlias = botAlias,
        userId = userID,
        inputText = rawUserInput)
    print(botResponse)
    
    label = botResponse["message"]
    print(label)
    
    if(label == "XXX"):
        print("LEX NO KEYWORD FOUND")
        response = {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin":"*","Content-Type":"application/json"},
            "body": [],
            "isBase64Encoded": False
            }
        return response
        
    nlabel = label.split(" ")
    nlabel = [x.strip(' ') for x in nlabel]    
    
    main_ans = []
    for tmp_lb in nlabel:
        tmp = search(tmp_lb)
        main_ans = main_ans + tmp

    print(main_ans)

    response = {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin":"*","Content-Type":"application/json"},
        "body": json.dumps(main_ans),
        "isBase64Encoded": False
        }

    return response