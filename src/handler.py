from src.crud.events import get_events, create_event


def events(event, context):
    if 'httpMethod' in event:
        if event['httpMethod'] == 'GET':
            return get_events(event, context)
        elif event['httpMethod'] == 'POST':
            return create_event(event, context)

    return {
        'statusCode': 405,
    }
