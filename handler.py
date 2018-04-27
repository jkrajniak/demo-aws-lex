import boto3
import json
import logging
import os
import urllib
import weather

bot_name = os.environ.get('BOT_NAME')
bot_alias = os.environ.get('BOT_ALIAS')

logger = logging.getLogger()
logger.setLevel(logging.ERROR)

def aws_lex_return_close(message_content, return_type='Fulfilled', session=None):
    out = {
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': return_type,
            'message': {
                'contentType': 'PlainText',
                'content': message_content
            }
        }
    }
    if session is not None:
        out['sessionAttributes'] = session
    return out

def populate_slots(event):
    """Gets the values from the slots.

    Args:
        event: then lambda event.
    
    Returns:
        The dictionary with the key being the slot name and the value derived by Lex.
    """

    slot_values = {}
    for slot_name, v in event['currentIntent']['slots'].items():
        slot_values[slot_name] = v

    # Populate resolved values
    for slot_name, v in event['currentIntent']['slotDetails'].items():
        if v is not None and len(v['resolutions']) > 0 and not slot_values.get(slot_name):
            slot_values[slot_name] = v['resolutions'][0]['value']

    return slot_values


def lex_handler(event, context):
    input_text = event['queryStringParameters']['text']
    user_id = event['queryStringParameters'].get('userId', 'anyrandom')

    lex_runtime = boto3.client('lex-runtime')
    try:
        response = lex_runtime.post_text(
            botName=bot_name,
            botAlias=bot_alias,
            userId=user_id,
            inputText=input_text)
    except Exception as ex:
        return {
            'statusCode': 500,
            'body': json.dumps(ex)
        }
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }


def get_weather(event, context):
    slot_values = populate_slots(event)
    location = slot_values.get('location')
    if location:
        wl = weather.Weather().lookup_by_=-location(location)
        if not wl:
            return aws_lex_return_close('Location {} not found'.format(location), 'Failed')
        output = (
            '{city} {country} (last-update: {date}) '
            ' {text} Temp: {temp}{temp_units} Wind: {speed}{speed_units}'
            ).format(city=wl.location.city,
                     country=wl.location.country,
                     date=wl.condition.date,
                     text=wl.condition.text,
                     temp=wl.condition.temp,
                     temp_units=wl.units.temperature,
                     speed=wl.wind.speed,
                     speed_units=wl.units.speed)
        return aws_lex_return_close(output)

    return aws_lex_return_close('Location {location} not found'.format(location=location), 'Failed')


def general_proxy_handler(event, context):
    """This will proxy all requests to the TEST_ENDPOINT."""
    outside_http = os.environ.get('TEST_ENDPOINT')

    logger.info('general_setup event={} url={}'.format(event, outside_http))

    params = json.dumps(event).encode('utf8')
    logger.info('params={}'.format(params))

    req = urllib.request.Request(outside_http, data=params, headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(req)

    response_json = json.loads(response.read())
    logger.info('general_setup response={}'.format(response_json))

    return response_json