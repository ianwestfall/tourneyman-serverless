import json
import os
import uuid

import boto3
import time

import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
dynamodb = boto3.resource('dynamodb')


def get_events(event, context):
    print('Logging a call to get_events')
    body = {
        "message": "Events GET function successfully called. ",
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response


def create_event(event, context):
    # Validate the input and extract the required data.
    # TODO: Make sure required fields exist and dates are in the correct format.
    # TODO: Integrate with Cognito so that the calling user can be extracted and used in the created_by column.
    data = json.loads(event['body'])
    event_name = data['name']
    event_description = data['description']
    created_at = int(time.time() * 1000)

    # Create the new event.
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE_EVENTS'])
    table.put_item(
        Item={
            'eventId': str(uuid.uuid4()),
            'name': event_name,
            'description': event_description,
            'createdAt': created_at,
            'startDate': 0,
            'endDate': 100,
            'status': 0,
            'createdBy': 'basic_user',
            'tournaments': [],
        }
    )

    # Return that the creation was successful.
    return {
        'statusCode': 201,
    }
