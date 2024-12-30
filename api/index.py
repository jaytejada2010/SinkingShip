from django.core.wsgi import get_wsgi_application
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SinkingShip.settings')
application = get_wsgi_application()

def handler(event, context):
    # Adapt Vercel event to WSGI environment
    environ = {
        'REQUEST_METHOD': event['httpMethod'],
        'PATH_INFO': event['path'],
        'QUERY_STRING': event.get('queryStringParameters', ''),
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https' if event.get('headers', {}).get('x-forwarded-proto', '') == 'https' else 'http',
        'wsgi.input': event.get('body', ''),
        'wsgi.errors': None,
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
    }

    if 'headers' in event:
        for key, value in event['headers'].items():
            environ['HTTP_' + key.upper().replace('-', '_')] = value

    # Create a response function
    def start_response(status, headers):
        handler.status = status
        handler.headers = headers

    # Call the WSGI application
    result = application(environ, start_response)
    response_body = b''.join(result).decode('utf-8')

    # Return the response to Vercel
    return {
        'statusCode': int(handler.status.split()[0]),
        'headers': dict(handler.headers),
        'body': response_body,
    }