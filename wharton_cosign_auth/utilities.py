from django.conf import settings

import requests


def call_wisp_api(url=None, params=None):
    headers = {'Authorization': 'Token %s' % settings.WISP_TOKEN}
    try:
        response = requests.get(url, headers=headers, params=params).json()
    except ValueError as err:
        raise Exception('WISP did not return valid JSON. This may be due to WISP API being down.') from err
    return response
