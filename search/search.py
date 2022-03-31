import json
import boto3
import requests


def lambda_handler(event, context):
    es_endpoint = 'https://search-photos-gmr5cx5hqtvs3p5ro5fgepywmu.us-east-1.es.amazonaws.com/'
    es_url = es_endpoint + 'photos/_doc/'
    headers = {"Content-Type": "application/json"}
    es_master = 'test'
    es_psw = 'P@55w0rd'

    lex = boto3.client('lexv2-runtime')
    print(event)
    query = event['queryStringParameters']['q']
# some comment
    lex_response = lex.recognize_text(
        botId='ARBQLPJYQJ',
        botAliasId='TSTALIASID',
        localeId='en_US',
        sessionId="test_session",
        text=query
    )

    slots = ['query', 'queryTwo']
    keywords = []

    if len(lex_response['sessionState']['intent']['slots']) == 0:
        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                'Content-Type': 'application/json'
            },
            'body': json.dumps("The keyword is uncatched.")
        }

    for slot in slots:
        if lex_response['sessionState']['intent']['slots'][slot] != None:
            keywords.append(lex_response['sessionState']['intent']['slots'][slot]['value']['originalValue'])

    query_items = []
    for keyword in keywords:
        keyword = keyword.lower()
        query_items.append(keyword)
        if keyword[-3:] == 'ies':
            query_items.append(keyword[:-3] + 'y')
        if keyword[-2:] == 'es':
            query_items.append(keyword[:-2])
        if keyword[-1] == 's':
            query_items.append(keyword[:-1])

    print(query_items)

    img_list = set()
    for keyword in query_items:
        es_response = requests.get(es_url + ('_search?q={}'.format(keyword)), auth=(es_master, es_psw),
                                   headers=headers).json()
        es_src = es_response['hits']['hits']
        for photo in es_src:
            labels = [word.lower() for word in photo['_source']['labels']]
            if keyword in labels:
                objectKey = photo['_source']['objectKey']
                img_url = 'https://hw2-photos-b2.s3.amazonaws.com/' + objectKey
                img_list.add(img_url)

    if img_list:
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,GET',
                "Access-Control-Allow-Origin": "*",
                'Content-Type': 'application/json'
            },
            'body': json.dumps(list(img_list))
        }
    else:
        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                'Content-Type': 'application/json'
            },
            'body': json.dumps("No such photos.")
        }

