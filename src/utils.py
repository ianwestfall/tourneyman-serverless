from abc import ABC, abstractmethod


class AuthenticatedRequestHandler(ABC):
    """
    Utility class to standardize some request processing code.
    """
    @staticmethod
    def get_authenticated_user_claims(event):
        return event['requestContext']['authorizer']['claims']

    @abstractmethod
    def validate_data(self, event, authenticated_user_claims):
        pass

    @abstractmethod
    def process(self, authenticated_user_claims, data):
        pass

    def handle_request(self, event, context):
        # Retrieve the authenticated user claims.
        authenticated_user_claims = self.get_authenticated_user_claims(event)

        # Validate and return the relevant data.
        data = self.validate_data(event, authenticated_user_claims)

        return self.process(authenticated_user_claims, data)
