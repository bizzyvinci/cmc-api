import pytest
from requests import Session
from cmc_api import *

cmc = CoinMarketCap(sandbox=True)


def test_base_url(base_url):
    assert cmc.BASE_URL == base_url


def test_init_session():
    assert isinstance(cmc._init_session(cmc.api_key), Session)


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
