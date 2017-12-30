from src.crud.events import GetEventsHandler, CreateEventHandler


def events(event, context):
    if 'httpMethod' in event:
        handler = None

        if event['httpMethod'] == 'GET':
            handler = GetEventsHandler()
        elif event['httpMethod'] == 'POST':
            handler = CreateEventHandler()

        if handler:
            return handler.handle_request(event, context)

    return {
        'statusCode': 405,
    }
