import os
import logging
from requests import Session
from .exceptions import *

class CoinMarketCap:
    PRO_BASE_URL = 'https://pro-api.coinmarketcap.com/v1'
    SANDBOX_BASE_URL = 'https://sandbox-api.coinmarketcap.com/v1'
    SANDBOX_API_KEY = 'b54bcf4d-1bca-4e8e-9a24-22ff2c3d462c'
    API_KEY = os.getenv('CMC_PRO_API_KEY')
    categories = {
        'crypto': 'cryptocurrency',
        'exchange': 'exchange',
        'fiat': 'fiat',
    }

    def __init__(self, api_key=API_KEY, sandbox=False):
        if sandbox: 
            api_key = self.SANDBOX_API_KEY
            self.BASE_URL = self.SANDBOX_BASE_URL
        else:
            self.BASE_URL = self.PRO_BASE_URL
        if not api_key:
            message = "No key is provided"
            raise CMCAPIException(message)
        self.api_key = api_key
        self.session = self._init_session(api_key)

    @staticmethod
    def _init_session(api_key):
        session = Session()
        headers = {
            'X-CMC_PRO_API_KEY': api_key,
            'Accepts': 'application/json',
            'Accept-Encoding': 'deflate, gzip',
        }
        session.headers.update(headers)
        return session

    def _insert_cat(self, text, cat, options=['crypto', 'exchange', 'fiat']):
        if cat in options:
            return text.format(self.categories[cat])
        else:
            raise ValueError(
                "Invalid category ({}) provided. "
                "Valid options are: {{{}}}".format(cat, ','.join(options)))

    def _get_url(self, url, parameters={}):
        response = self.session.get(url, params=parameters)
        res = response.json()
        if response.status_code == 200:
            return res['data']
        else:
            error_message = res['status']['error_message']
            if response.status_code == 400:
                raise BadRequestException(error_message)
            elif response.status_code == 401:
                raise UnauthorizedException(error_message)
            elif response.status_code == 402:
                raise PaymentRequiredException(error_message)
            elif response.status_code == 403:
                raise ForbiddenException(error_message)
            elif response.status_code == 429:
                raise TooManyRequestsException(error_message)
            elif response.status_code == 500:
                raise InternalServerErrorException(error_message)
            else:
                error_message = "Unknown response error:{}:{}".format(
                          response.status_code, error_message)
                raise CMCAPIException(error_message)

    @staticmethod
    def _check_datetime_format(date_):
        """
        Check if date_ is ISO8601 format (eg. 2018-06-06T01:46:40Z)
        or Unix time (eg. 1528249600).
        """
        pass

    def map(self, cat='crypto', **kwargs):
        url = self._insert_cat(self.BASE_URL + '/{}/map', cat)
        return self._get_url(url, kwargs)

    def listings(self, cat='crypto', **kwargs):
        url = self._insert_cat(self.BASE_URL + '/{}/listings/latest', cat)
        return self._get_url(url, kwargs)

    