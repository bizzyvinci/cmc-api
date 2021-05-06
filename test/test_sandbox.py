import pytest
from datetime import date, datetime
from requests import Session
from cmc_api import *
from cmc_api.coinmarketcap import parse_param, parameters_parser


def test_parse_param():
    assert parse_param('id', 4) == 4
    assert parse_param('symbol', 'BTC') == 'BTC'
    assert parse_param('price_min', 250.50) == 250.50
    assert parse_param('symbol', ['BTC', 'ETH', 'USD']) == 'BTC,ETH,USD'
    assert parse_param('id', (1,2,3)) == '1,2,3'
    assert parse_param('date', datetime(2020,1,1)) == '2020-01-01T00:00:00'
    assert parse_param('date', date(2020,1,1)) == '2020-01-01'
    # Set is unordered,
    # therefore it could be 'id,name' or 'name,id'.
    result = parse_param('aux', {'id', 'name'})
    assert isinstance(result, str)
    assert  'id' in result and 'name' in result
    with pytest.raises(ValueError):
        parse_param('x', {1:2, 3:4})


def test_parameters_parser():
    parser = parameters_parser('cat', 'year')
    def func(cat, year='2020', **parameters):
        return cat, year, parameters
    function = parser(func)
    cat, year, parameters = function('a', year=[2021], id=[1,2,3])
    assert cat == 'a'
    assert year == [2021]
    assert parameters['id'] == '1,2,3'


cmc = CoinMarketCap(root='sandbox')


def test_base_url(base_url):
    assert cmc.BASE_URL == base_url


def test_init_session():
    session = cmc._init_session(cmc.api_key)
    assert isinstance(session, Session)
    assert 'X-CMC_PRO_API_KEY' in session.headers
    assert session.headers['Accepts'] == 'application/json'


def test_insert_cat(base_url):
    url = cmc._insert_cat(base_url+'{}', 'crypto')
    assert url == base_url+'cryptocurrency'


def test_insert_cat_bad(base_url):
    with pytest.raises(ValueError):
        url = cmc._insert_cat(base_url+'{}', 'not_in_categories')


def test_get_url(base_url):
    result = cmc._get_url(base_url+'/cryptocurrency/listings/latest')
    assert isinstance(result, list)
    assert len(result) > 0
    assert isinstance(result[0], dict)


def test_get_url_bad(base_url):
    with pytest.raises(Exception):
        result = cmc._get_url(base_url+'/no_real_endpoint/raise_error')


def test_map_crypto():
    result = cmc.map()
    assert isinstance(result, list)
    assert result[0]['id'] == 1
    assert result[1]['symbol'] == 'LTC'


def test_map_exchange():
    result = cmc.map('exchange')
    assert isinstance(result, list)
    assert result[0]['id'] == 16
    assert result[1]['name'] == 'C-CEX'


def test_map_fiat():
    result = cmc.map('fiat')
    assert isinstance(result, list)
    assert result[0]['symbol'] == 'USD'
    assert result[1]['id'] == 2782


def test_map_with_parameters():
    parameters = {
        'limit': 5,
        'sort': 'cmc_rank',
    }
    result = cmc.map(**parameters)
    assert len(result) == 5
    for i,x in enumerate(result):
        assert x['rank'] == i+1


def test_map_with_kw_parameters():
    slug = ['binance', 'cryptsy', 'poloniex', 'luno', 'wex']
    result = cmc.map('exchange', slug=slug)
    assert len(result) == len(slug)
    for x in result:
        assert x['slug'] in slug


def test_map_bad_cat():
    with pytest.raises(ValueError):
        result = cmc.map('not_in_categories')


def test_listings_crypto():
    result = cmc.listings()
    assert isinstance(result, list)
    for x in ('id', 'name', 'symbol', 'max_supply', 'cmc_rank', 'quote'):
        assert x in result[0]


def test_listings_exchange():
    result = cmc.listings('exchange')
    assert isinstance(result, list)
    for x in ('id', 'name', 'slug', 'num_market_pairs', 'last_updated', 'quote'):
        assert x in result[0]


def test_listings_bad_cat():
    with pytest.raises(ValueError):
        result = cmc.listings('not_in_categories')


def test_info():
    result = cmc.info(id='1,2,4')
    assert isinstance(result['1'], dict)
    assert isinstance(result['2'], dict)
    assert isinstance(result['4'], dict)


def test_info_exchange():
    result = cmc.info(id=16)
    assert isinstance(result['16'], dict)
    for x in ('id', 'urls', 'name', 'slug', 'date_launched'):
        assert x in result['16']


def test_info_bad_cat():
    with pytest.raises(ValueError):
        result = cmc.info('not_in_categories')


def test_key_info():
    result = cmc.key_info()
    assert 'plan' in result
    assert 'usage' in result
    assert isinstance(result['plan'], dict)
    assert isinstance(result['usage'], dict)
