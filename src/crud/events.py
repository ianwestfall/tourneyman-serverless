import json
import os
import time
import uuid

import boto3
from boto3.dynamodb.conditions import Key

from src.utils import AuthenticatedRequestHandler

dynamodb = boto3.resource('dynamodb')
DYNAMODB_TABLE_EVENTS = dynamodb.Table(os.environ['DYNAMODB_TABLE_EVENTS'])


class GetEventsHandler(AuthenticatedRequestHandler):
    def validate_data(self, event, authenticated_user_claims):
        pass

    def process(self, authenticated_user_claims, data):
        events = DYNAMODB_TABLE_EVENTS.query(
            KeyConditionExpression=Key('createdBy').eq(authenticated_user_claims['cognito:username'])
        )['Items']

        # TODO: Return the events in a more complete fashion.
        body = {
            "message": "Events GET function successfully called. ",
            "events": ['Created By: %s, UUID: %s, Name: %s' % (event['createdBy'], event['eventId'], event['name'])
                       for event in events],
        }

        response = {
            "statusCode": 200,
            "body": json.dumps(body)
        }

        return response


class CreateEventHandler(AuthenticatedRequestHandler):
    def validate_data(self, event, authenticated_user_claims):
        data = json.loads(event['body'])
        event_id = str(uuid.uuid4())
        event_name = data['name']
        event_description = data['description']
        created_at = int(time.time() * 1000)
        created_by = authenticated_user_claims['cognito:username']
        # TODO: Pull out start and end date

        validated_data = {
            'event_id': event_id,
            'event_name': event_name,
            'event_description': event_description,
            'created_at': created_at,
            'created_by': created_by,
        }

        return validated_data

    def process(self, authenticated_user_claims, data):
        # Create the new event.
        DYNAMODB_TABLE_EVENTS.put_item(
            Item={
                'eventId': data['event_id'],
                'name': data['event_name'],
                'description': data['event_description'],
                'createdAt': data['created_at'],
                'createdBy': data['created_by'],
                'startDate': 0,
                'endDate': 100,
                'status': 0,
                'tournaments': [],
                'versionId': 0,
            }
        )

        # Return that the creation was successful.
        return {
            'statusCode': 201,
        }
