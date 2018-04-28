import json

from src.utils import AuthenticatedRequestHandler


class GetEventsHandler(AuthenticatedRequestHandler):
    def validate_data(self, event, authenticated_user_claims):
        pass

    def process(self, authenticated_user_claims, data):
        body = {
            "message": "Events GET function successfully called. ",
        }

        response = {
            "statusCode": 200,
            "body": json.dumps(body)
        }

        return response


class CreateEventHandler(AuthenticatedRequestHandler):
    def validate_data(self, event, authenticated_user_claims):
        pass

    def process(self, authenticated_user_claims, data):
        return {
            'statusCode': 201,
        }
