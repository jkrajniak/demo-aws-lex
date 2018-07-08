import os
import logging




def main():

    os.environ.update({
        'DYNAMODB_TABLENAME': 'walutobot-ng-dev2-WalutoBot',
        'DYNAMODB_CURRENCY_TABLENAME': 'walutobot-ng-dev2-CurrencyRate',
        'BOT_TOKEN': 'xoxb-312074669781-5qTguhYzfqEXWvromFTUWjbg',
        'CURRENCY_PROVIDER': 'IK',
        'BUCKET_CURRENCY_PLOTS': 'walutobot-ng-dev2-eu-west-1-currency-plots-bucket',
        'REGION': 'eu-west-1',
        'LOG_LEVEL': 'DEBUG',
        'TEST_ENDPOINT': 'http://868dc51d.ngrok.io',
        'DEBUG': 'True'
    })

    import handler
    logging.getLogger().setLevel(logging.DEBUG)
    r = handler.handle_fetch_currency_rates_and_notify('', '')
    print(r)
    # r = handler.handle_average_updates('', '')
    # print(r)

if __name__ == '__main__':
    main()
