import functools
import logging
import os
from datetime import datetime, date
from requests import Session
from .exceptions import *


def parse_param(key, value):
    """
    Parse value to int or str,
    which are the valid datatype for request parameters.
    """
    if isinstance(value, (str, int, float)):
        return value
    elif isinstance(value, (list, tuple, set)):
        return ','.join([str(x) for x in value])
    elif isinstance(value, (datetime, date)):
        return value.isoformat()
    else:
        raise ValueError(
            'Got an invalid datatype for parameter {}. Try converting it to '
            'str, int, float, list, tuple, set, datetime or date.'.format(key))


def parameters_parser(*excluded_parameters):
    """
    This decorator parses parameters for requests.

    Parameters:
    *excluded_parameters: parameters that are basic to function,
        and therefore to be excluded from the parameters for requests.
    """
    def decorator(function):
        @functools.wraps(function)
        def wrapper(*args, **parameters):
            for key,value in parameters.items():
                if key not in excluded_parameters:
                    parameters[key] = parse_param(key, value)
            return function(*args, **parameters)
        return wrapper
    return decorator


class CoinMarketCap:
    """
    A class to initiate coinmarketcap api.

    Parameters
    ----------
    api_key: str, default os.getenv('CMC_PRO_API_KEY')
        API key to use with pro-api
    root: str, default 'pro'
        The root of api e.g 'pro' for `pro-api`
        and 'sandbox' for `sandox-api`

    Returns
    -------
    object

    Attributes
    ----------
    CoinMarketCap.api_key: str
        API KEY.
    CoinMarketCap.session: requests.Session
        Session used for requests.
    """
    _categories = {
        'crypto': 'cryptocurrency',
        'exchange': 'exchange',
        'fiat': 'fiat',
        'key': 'key',
        'global-metrics': 'global-metrics',
    }

    def __init__(self, api_key=os.getenv('CMC_PRO_API_KEY'), root='pro'):
        self.BASE_URL = 'https://{}-api.coinmarketcap.com/v1'.format(root)
        if root=='pro':
            if not api_key:
                message = "No key is provided for pro-api."
                raise CMCAPIException(message)
        else:
            api_key = None
        self.api_key = api_key
        self.session = self._init_session(api_key)

    @staticmethod
    def _init_session(api_key):
        """Initialize session which would be used for requests."""
        session = Session()
        headers = {
            'Accepts': 'application/json',
            'Accept-Encoding': 'deflate, gzip',
        }
        if api_key is not None:
            headers['X-CMC_PRO_API_KEY'] = api_key
        session.headers.update(headers)
        return session

    def _insert_cat(self, text, cat, options=['crypto', 'exchange']):
        """Insert cat into text if in options."""
        if cat in options:
            return text.format(self._categories[cat])
        else:
            raise ValueError(
                "Invalid category ({}) provided. "
                "Valid options are: {{{}}}".format(cat, ','.join(options)))

    def _get_url(self, url, parameters={}):
        """Get Response.json()['data']."""
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

    @parameters_parser('cat')
    def map(self, cat='crypto', **parameters):
        """
        Get ID map for cryptocurrency, exchange or fiat.

        Parameters
        ----------
        cat: {'crypto', 'exchange', 'fiat'}, default 'crypto'
            The category to get map for.
        \*\*parameters: keyword arguments
            Parameters to include in the request.
            listing_status: str or sequence of strs, default 'active'
                option: {'active', 'inactive', 'untracked'}.
                cat: {'crypto', 'exchange'}
            slug: str or sequence of strs
                cat: {'exchange'}
            start: int, default 1
                cat: {'crypto', 'exchange', fiat'}
            limit: int {1...5000}, optional
                cat: {'crypto', 'exchange', 'fiat'}
            sort: str, default 'id'
                option: {'id', 'cmc_rank', 'name', 'volume_24h'}
                cat: {'crypto', 'exchange', 'fiat'}
            symbol: str or sequence of strs, optional
                cat: {'crypto'}
            crypto_id: str
                cat: {'exchange'}
            include_metals: bool, default False
                cat: {'fiat'}
            aux: default "platform,first_historical_data,last_historical_data,is_active"
                all: platform,first_historical_data,last_historical_data,is_active,status
                cat: {'crypto', 'exchange'}
        
        Returns
        -------
        data: list

        References
        ----------
        .. [1] `/v1/cryptocurrency/map
            <https://coinmarketcap.com/api/documentation/v1/#operation/getV1CryptocurrencyMap>`_
        .. [2] `/v1/exchange/map
            <https://coinmarketcap.com/api/documentation/v1/#operation/getV1ExchangeMap>`_
        .. [3] `/v1/fiat/map
            <https://coinmarketcap.com/api/documentation/v1/#operation/getV1FiatMap>`_
        """
        url = self._insert_cat(self.BASE_URL + '/{}/map', cat,
              ['crypto', 'exchange', 'fiat'])
        return self._get_url(url, parameters)

    @parameters_parser('cat')
    def listings(self, cat='crypto', **parameters):
        """
        Get latest listings for cryptocurrency or exchange.

        Parameters
        ----------
        cat: {'crypto', 'exchange'}, default 'crypto'
            The category to get listings for.
        \*\*parameters: keyword arguments
            Parameters to include in the request.
            start: int, default 1
                cat: {'crypto', 'exchange'}
            limit: int {1...5000}, default 100
                cat: {'crypto', 'exchange'}
            price_min: int or float {0...1e17}, optional
                cat: {'crypto'}
            price_max: int or float {0...1e17}, optional
                cat: {'crypto'}
            market_cap_min: int or float {0...1e17}, optional
                cat: {'crypto'}
            market_cap_max: int or float {0...1e17}, optional
                cat: {'crypto'}
            volume_24h_min: int or float {0...1e17}, optional
                cat: {'crypto'}
            volume_24h_max: int or float {0...1e17}, optional
                cat: {'crypto'}
            circulating_supply_min: int or float {0...1e17}, optional
                cat: {'crypto'}
            circulating_supply_max: int or float {0...1e17}, optional
                cat: {'crypto'}
            percent_change_24h_min: int or float {0...1e17}, optional
                cat: {'crypto'}
            percent_change_24h_max: int or float {0...1e17}, optional
                cat: {'crypto'}
            convert: str, optional
                cat: {'crypto', 'exchange'}
            convert_id: str, optional
                cat: {'crypto', 'exchange'}
            sort: str, default 'market_cap'
                option: {'name', 'symbol', 'date_added', 'market_cap',
                    'market_cap_by_total_supply_strict', 'volume_7d',
                    'volume_30d', 'volume_24h',  'volume_24h_adjusted',
                    'exchange_score'}
                cat: {'crypto', 'exchange'}
            sort_dir: {'asc', 'desc'}, optional
                cat: {'crypto', 'exchange'}
            cryptocurrency_type: {'all', 'coins', 'tokens'}, default 'all'
                cat: {'crypto'}
            tag: str, default 'all'
                option: {'all', 'defi', 'filesharing'}
                cat: {'crypto'}
            market_type: str, default 'all'
                option: {'fees','no_fees', 'all'}
                cat: {'exchange'}
            aux: str or sequence of str
                cat: {'crypto', 'exchange'}

        Returns
        -------
        data: list

        References
        ----------
        .. [1] `/v1/cryptocurrency/listings/latest
            <https://coinmarketcap.com/api/documentation/v1/#operation/getV1CryptocurrencyListingsLatest>`_
        .. [2] `/v1/exchange/listings/latest
            <https://coinmarketcap.com/api/documentation/v1/#operation/getV1ExchangeListingsLatest>`_
        """
        url = self._insert_cat(self.BASE_URL + '/{}/listings/latest', cat)
        return self._get_url(url, parameters)

    @parameters_parser('cat')
    def historical_listings(self, cat='crypto', **parameters):
        """
        Get latest listings for cryptocurrency or exchange.

        Parameters
        ----------
        cat: {'crypto', 'exchange'}, default 'crypto'
            The category to get historical for.
        \*\*parameters:  keyword arguments
            Parameters to include in the request.
            
        Returns
        -------
        data: list

        References
        ----------
        .. [1] `/v1/cryptocurrency/listings/historical
            <https://coinmarketcap.com/api/documentation/v1/#operation/getV1CryptocurrencyListingsHistorical>`_
        .. [2] `/v1/exchange/listings/historical
            <https://coinmarketcap.com/api/documentation/v1/#operation/getV1ExchangeListingsHistorical>`_
        """
        url = self._insert_cat(self.BASE_URL + '/{}/listings/historical', cat)
        return self._get_url(url, parameters)

    @parameters_parser('cat')
    def info(self, cat='crypto', **parameters):
        """
        Get Metadata for cryptocurrency or exchange.

        Parameters
        ----------
        cat: {'crypto', 'exchange', 'key'}, default 'crypto'
            The category to get info for.
        \*\*parameters:  keyword arguments
            Parameters to include in the request.
            id or slug or symbol is mandatory
            id: str or sequence of strs
                cat: {'crypto', 'exchange'}
            slug: str or sequence of strs
                cat: {'crypto', 'exchange'}
            symbol: str or sequence of strs
                cat: {'crypto'}
            aux: str or sequence of str
                cat: {'crypto', 'exchange'}
        
        Returns
        -------
        data: dict

        References
        ----------
        .. [1] `/v1/cryptocurrency/info
            <https://coinmarketcap.com/api/documentation/v1/#operation/getV1CryptocurrencyInfo>`_
        .. [2] `/v1/exchange/info
            <https://coinmarketcap.com/api/documentation/v1/#operation/getV1ExchangeInfo>`_
        .. [3] `/v1/key/info
            <https://coinmarketcap.com/api/documentation/v1/#operation/getV1KeyInfo>`_
        """
        url = self._insert_cat(self.BASE_URL + '/{}/info', cat, 
              ['crypto', 'exchange', 'key'])
        return self._get_url(url, parameters)

    def key_info(self):
        """
        Get API key details and usage stats.
        """
        return self.info('key')

    @parameters_parser('cat')
    def quotes(self, cat='crypto', **parameters):
        """
        Get latest quotes for cryptocurrency or exchange.

        Parameters
        ----------
        cat: {'crypto', 'exchange', 'global-metrics'}, default 'crypto'
            The category to get quotes for.
        \*\*parameters:  keyword arguments
            Parameters to include in the request.
            
        Returns
        -------
        data: dict

        References
        ----------
        .. [1] `/v1/cryptocurrency/quotes/latest
            <https://coinmarketcap.com/api/documentation/v1/#operation/getV1CryptocurrencyQuotesLatest>`_
        .. [2] `/v1/exchange/quotes/latest
            <https://coinmarketcap.com/api/documentation/v1/#operation/getV1ExchangeQuotesLatest>`_
        .. [3] `/v1/global-metrics/quotes/latest
            <https://coinmarketcap.com/api/documentation/v1/#operation/getV1GlobalmetricsQuotesLatest>`_
        """
        url = self._insert_cat(self.BASE_URL + '/{}/quotes/latest', cat,
              ['crypto', 'exchange', 'global-metrics'])
        return self._get_url(url, parameters)

    @parameters_parser('cat')
    def historical_quotes(self, cat='crypto', **parameters):
        """
        Get historical quotes for cryptocurrency or exchange.

        Parameters
        ----------
        cat: {'crypto', 'exchange', 'global-metrics'}, default 'crypto'
            The category to get historical quotes for.
        \*\*parameters:  keyword arguments
            Parameters to include in the request.
            
        Returns
        -------
        data: dict

        References
        ----------
        .. [1] `/v1/cryptocurrency/quotes/historical
            <https://coinmarketcap.com/api/documentation/v1/#operation/getV1CryptocurrencyQuotesHistorical>`_
        .. [2] `/v1/exchange/quotes/historical
            <https://coinmarketcap.com/api/documentation/v1/#operation/getV1ExchangeQuotesHistorical>`_
        .. [3] `/v1/global-metrics/quotes/historical
            <https://coinmarketcap.com/api/documentation/v1/#operation/getV1GlobalmetricsQuotesHistorical>`_
        """
        url = self._insert_cat(self.BASE_URL + '/{}/quotes/historical', cat,
              ['crypto', 'exchange', 'global-metrics'])
        return self._get_url(url, parameters)
