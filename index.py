import json
import boto3
import requests
from datetime import *


def create_photo_obj(bucket, key, labels, customLabels):
    return {
        'bucket': bucket,
        'objectKey': key,
        'createdTimestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'labels': [x['Name'] for x in labels] + customLabels
    }


def lambda_handler(event, context):
    es_endpoint = 'https://search-photos-gmr5cx5hqtvs3p5ro5fgepywmu.us-east-1.es.amazonaws.com/'
    es_url = es_endpoint + 'photos/_doc/'
    headers = {"Content-Type": "application/json"}
    es_master = 'test'
    es_psw = 'P@55w0rd'

    rek = boto3.client('rekognition')
    s3_client = boto3.client('s3')
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        size = record['s3']['object']['size']
        print('buck', bucket)
        print('key', key)
        labels = rek.detect_labels(
            Image={
                'S3Object': {
                    'Bucket': bucket,
                    'Name': key
                }
            },
            MaxLabels=12
        )
        metadata = s3_client.head_object(
            Bucket=bucket,
            Key=key
        )
        print('metadata:', metadata)
        customLabels = []
        if 'x-amz-meta-customlabels' in metadata['ResponseMetadata']['HTTPHeaders']:
            customLabels = metadata['ResponseMetadata']['HTTPHeaders']['x-amz-meta-customlabels'].split(',')
        print('customLabels:', customLabels)

        # get labels
        # create photos
        obj = create_photo_obj(bucket, key, labels['Labels'], customLabels)
        print(obj)
        obj = json.dumps(obj)

        try:
            req = requests.post(es_url, data=obj, auth=(es_master, es_psw), headers=headers)
        except ClientError as e:
            raise ('Error', e.response['Error']['Message'])
        else:
            print(req.text)
            return json.loads(req.text)

    return {
        'statusCode': 200,
        'body': obj
    }