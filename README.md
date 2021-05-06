# cmc-api

## Unofficial wrapper for [coinmarketcap api](https://coinmarketcap.com/api)

This is up to date for coinmarketcap pro-api v1.27.0.

### Endpoints and their associated function
| Endpoint							| Method			|
| --------------------------------- | ----------------- |
| /v1/cryptocurrency/map			| map()				|
| /v1/cryptocurrency/info			| info()			|
| /v1/cryptocurrency/listings/latest| listings()		|
| /v1/cryptocurrency/listings/historical| historical_listings() |
| /v1/cryptocurrency/quotes/latest 	| quotes()			|
| /v1/cryptocurrency/quotes/historical	| historical_quotes()	|
| /v1/cryptocurrency/market-pairs/latest| -				|
| /v1/cryptocurrency/ohlcv/latest 	| -					|
| /v1/cryptocurrency/ohlcv/historical	| -				|
| /v1/cryptocurrency/price-performance-stats/latest	| - |
| /v1/exchange/map					| map('exchange')	|
| /v1/exchange/info					| info('exchange')	|
| /v1/exchange/listings/latest		| listings('exchange')	|
| /v1/exchange/listings/historical	| historical_listings('exchange')	|
| /v1/exchange/quotes/latest		| quotes('exchange')|
| /v1/exchange/quotes/historical	| historical_quotes('exchange')	|
| /v1/exchange/market-pairs/latest	| -					|
| /v1/global-metrics/quotes/latest	| quotes('global-metrics')	|
| /v1/global-metrics/quotes/historical	| historical_quotes('global-metrics')	|
| /v1/tools/price-conversion		| -					|
| /v1/blockchain/statistics/latest	| -					|
| /v1/fiat/map						| map('fiat')		|
| /v1/partners/flipside-crypto/fcas/listings/latest	| -	|
| /v1/partners/flipside-crypto/fcas/quotes/latest	| -	|
| /v1/key/info						| key_info() or info('key')	|

**Note**: Every method takes in parameters as kwargs. `-` would be added later.

### Installation
#### Method 1
```bash
pip install cmc-api
```

#### Method 2
```bash
pip install git+https://github.com/bizzyvinci/cmc-api.git
```

#### Method 3
```bash
git clone https://github.com/bizzyvinci/cmc-api.git
cd cmc-api
python setup.py install
```

### Quick start guide
Quick start with sandbox.
```python
from cmc_api import CoinMarketCap

cmc = CoinMarketCap(root='sandbox')

# List all cryptocurrency in coinmarketcap
cmc.map()

# Get latest listings
cmc.listings()
```

To use pro-api, A registered key from [coinmarketcap](https://coinmarketcap.com/api) is required. This key can be added to environment variable as `CMC_PRO_API_KEY`. After the api can be used as:
```python
cmc = CoinMarketCap()
```

If `CMC_PRO_API_KEY` is not in environment variable, then the key needs to be passed as argument.
```python
cmc = CoinMarketCap(YOUR_API_KEY)
```

### Passing parameters
Some functions require parameters to send along with the request. This can be passed in as keyword arguments.

#### keyword arguments
```python
cmc.info('exchange', id=[2,270])
```

#### kwargs as dict
```python
parameters = {
	'price_min': 10000,
	'price_max': 30000,
	'convert': ['USD', 'EUR', 'GBP']
}
cmc.listings(**parameters)
```

[Documentation here]()
