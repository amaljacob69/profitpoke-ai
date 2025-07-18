from flask import Flask, request, render_template, flash, make_response, jsonify, redirect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired
from kiteconnect import KiteConnect
import requests
import json
import os
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from uuid import uuid4
import base64
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(32))

# API keys from environment variables
KITE_API_KEY = os.environ.get('KITE_API_KEY')
KITE_API_SECRET = os.environ.get('KITE_API_SECRET')
GROK_API_KEY = os.environ.get('GROK_API_KEY')

if not all([KITE_API_KEY, KITE_API_SECRET, GROK_API_KEY]):
    raise ValueError("Missing API keys. Set KITE_API_KEY, KITE_API_SECRET, and GROK_API_KEY.")

# Initialize Kite Connect with custom HTTP session
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504], allowed_methods=["GET", "POST"])
session.mount('https://', HTTPAdapter(max_retries=retries))
kite = KiteConnect(api_key=KITE_API_KEY, timeout=15)
kite.session = session

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

cache = Cache(app, config={
    'CACHE_TYPE': 'SimpleCache' if not os.environ.get('REDIS_URL') else 'RedisCache',
    'CACHE_REDIS_URL': os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
})

app.static_folder = 'static'

@app.after_request
def add_security_headers(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "style-src 'self' https://cdn.jsdelivr.net; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src 'self' data:; "
        "connect-src 'self' https://api.x.ai"
    )
    return response

@app.route('/static/manifest.json')
def serve_manifest():
    manifest = {
        "name": "ProfitPoke AI - Smart Stock Insights",
        "short_name": "ProfitPoke AI",
        "description": "AI-powered stock recommendations for the Indian market",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#667eea",
        "theme_color": "#667eea",
        "orientation": "portrait",
        "scope": "/",
        "lang": "en",
        "icons": [
            {
                "src": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTkyIiBoZWlnaHQ9IjE5MiIgdmlld0JveD0iMCAwIDE5MiAxOTIiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxOTIiIGhlaWdodD0iMTkyIiByeD0iMzIiIGZpbGw9InVybCgjZ3JhZGllbnQwX2xpbmVhcl8xXzEpIi8+CjxwYXRoIGQ9Ik05NiA0OEM3NC41IDQ4IDU2IDY2LjUgNTYgODhWMTQ0QzU2IDE2NS41IDc0LjUgMTg0IDk2IDE4NCMxMTcuNSAxODQgMTM2IDE2NS41IDEzNiAxNDRWODhDMTM2IDY2LjUgMTE3LjUgNDggOTYgNDhaIiBmaWxsPSJ3aGl0ZSIvPgo8cGF0aCBkPSJNOTYgNzJDODcuMiA3MiA4MCA3N9YyIDgwIDg4Vjk2SDExMlY4OEMxMTIgNzkuMiAxMDQuOCA3MiA5NiA3MloiIGZpbGw9IiM2NjdlZWEiLz4KPGF0aCBkPSJNODAgMTA0VjE0NEM4MCA1Mi44IDg3LjIgMTYwIDk2IDE2MEMxMDQuOCAxNjAgMTEyIDE1Mi44IDExMiAxNDRWMTA0SDgwWiIgZmlsbD0iIzc2NGJhMiIvPgo8ZGVmcz4KPGxpbmVhckdyYWRpZW50IGlkPSJncmFkaWVudDBfbGluZWFyXzFfMSIgeDE9IjAiIHkxPSIwIiB4Mj0iMTkyIiB5Mj0iMTkyIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+CjxzdG9wIHN0b3AtY29sb3I9IiM2NjdlZWEiLz4KPHN0b3Agb2Zmc2V0PSIxIiBzdG9wLWNvbG9yPSIjNzY0YmEyIi8+CjwvbGluZWFyR3JhZGllbnQ+CjwvZGVmcz4KPC9zdmc+",
                "sizes": "192x192",
                "type": "image/svg+xml"
            },
            {
                "src": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNTEyIiBoZWlnaHQ9IjUxMiIgdmlld0JveD0iMCAwIDUxMiA1MTIiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSI1MTIiIGhlaWdodD0iNTEyIiByeD0iODQiIGZpbGw9InVybCgjZ3JhZGllbnQwX2xpbmVhcl8xXzEpIi8+CjxwYXRoIGQ9Ik0yNTYgMTI4QzE5OC41IDEyOCAxNTIgMTc0LjUgMTUyIDIzMlYzODRDMTUyIDQ0MS41IDE5OC41IDQ4OCAyNTYgNDg4QzMxMy41IDQ4OCAzNjAgNDQxLjUgMzYwIDM4NFYyMzJDMzYwIDE3NC41IDMxMy41IDEyOCAyNTYgMTI4WiIgZmlsbD0id2hpdGUiLz4KPGF0aCBkPSJNMjU2IDE5MkMyMzMuMiAxOTIgMjE0IDIxMS4yIDIxNCAyMzRWMjU2SDI5OFYyMzRDMjk4IDIxMS4yIDI3OC44IDE5MiAyNTYgMTkyWiIgZmlsbD0iIzY2N2VlYSIvPgo8cGF0aCBkPSJNMjE0IDI3OFYzODRDMjE0IDQwNi44IDIzMy4yIDQyNiAyNTYgNDI2QzI3OC44IDQyNiAyOTggNDA2LjggMjk4IDM4NFYyNzhIMjE0WiIgZmlsbD0iIzc2NGJhMiIvPgo8ZGVmcz4KPGxpbmVhckdyYWRpZW50IGlkPSJncmFkaWVudDBfbGluZWFyXzFfMSIgeDE9IjAiIHkxPSIwIiB4Mj0iNTEyIiB5Mj0iNTEyIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+CjxzdG9wIHN0b3AtY29sb3I9IiM2NjdlZWEiLz4KPHN0b3Agb2Zmc2V0PSIxIiBzdG9wLWNvbG9yPSIjNzY0YmEyIi8+CjwvbGluZWFyR3JhZGllbnQ+CjwvZGVmcz4KPC9zdmc+",
                "sizes": "512x512",
                "type": "image/svg+xml"
            }
        ]
    }
    return json.dumps(manifest), 200, {'Content-Type': 'application/json'}

@app.route('/health')
def health_check():
    """Health check endpoint for Cloud Run"""
    return jsonify({
        'status': 'healthy',
        'service': 'profitpoke-api',
        'version': '1.0.0'
    }), 200

class RecommendationForm(FlaskForm):
    price_range = SelectField('Price Range (INR)', choices=[
        ('None', 'None'),
        ('0-100', '0-100'),
        ('100-200', '100-200'),
        ('200-500', '200-500'),
        ('500-1000', '500-1000'),
        ('1000+', '1000+')
    ], validators=[DataRequired()])
    time_horizon = SelectField('Time Horizon', choices=[
        ('None', 'None'),
        ('short-term', 'Short-term'),
        ('medium-term', 'Medium-term'),
        ('long-term', 'Long-term')
    ], validators=[DataRequired()])
    risk_level = SelectField('Risk Level', choices=[
        ('None', 'None'),
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], validators=[DataRequired()])
    submit = SubmitField('Get Recommendations')

class StockRecommendationService:
    def __init__(self, kite):
        self.kite = kite
        # Static sector mapping (replace with external source in production)
        self.sector_mapping = {
            'Technology': ['TRIGYN', 'SAKSOFT', 'MPSLTD', 'XCHANGING', 'KERNEX', 'MOSCHIP', 'RSYSTEMS', 'SUBEX'],
            'Financial Services': ['HDFCBANK', 'ICICIBANK', 'SBIN', 'KOTAKBANK'],
            'Healthcare': ['SUNPHARMA', 'DRREDDY', 'CIPLA', 'DIVISLAB'],
            'Consumer Goods': ['HINDUNILVR', 'ITC', 'NESTLEIND', 'BRITANNIA'],
            'Energy': ['RELIANCE', 'ONGC', 'BPCL', 'GAIL'],
            'Automobiles': ['MARUTI', 'TATAMOTORS', 'M&M', 'BAJAJ-AUTO'],
            'Metals & Mining': ['TATASTEEL', 'JSWSTEEL', 'HINDALCO', 'VEDL'],
            'Real Estate': ['DLF', 'GODREJPROP', 'OBEROIRLTY', 'PRESTIGE'],
            'Telecommunications': ['BHARTIARTL', 'IDEA', 'RELIANCE'],
            'Infrastructure': ['LT', 'ADANIPORTS', 'GRASIM', 'ULTRACEMCO']
        }

    @cache.memoize(timeout=86400)  # Cache for 24 hours
    def get_nse_instruments(self):
        try:
            instruments = self.kite.instruments('NSE')
            logger.info("Successfully fetched NSE instruments")
            return instruments
        except Exception as e:
            logger.error(f"Error fetching NSE instruments: {str(e)}")
            return []

    def get_top_gaining_sectors(self):
        try:
            instruments = self.get_nse_instruments()
            symbols = [inst['tradingsymbol'] for inst in instruments if inst['segment'] == 'NSE']
            if not symbols:
                logger.error("No NSE instruments available")
                return []

            # Batch symbols to avoid 414 Request-URI Too Large
            batch_size = 500
            market_data = {}
            for i in range(0, len(symbols), batch_size):
                batch = [f'NSE:{symbol}' for symbol in symbols[i:i + batch_size]]
                try:
                    market_data.update(self.kite.quote(batch))
                except Exception as e:
                    logger.warning(f"Error fetching quotes for batch {i//batch_size + 1}: {str(e)}")
                    continue

            # Calculate sector performance
            sector_gains = {}
            for symbol in symbols:
                quote = market_data.get(f'NSE:{symbol}', {})
                if not quote or 'last_price' not in quote or 'price_change' not in quote:
                    continue
                percent_change = (quote['price_change'] / (quote['last_price'] - quote['price_change'])) * 100 if quote['last_price'] != quote['price_change'] else 0
                # Find sector for the symbol
                sector = None
                for sec, syms in self.sector_mapping.items():
                    if symbol in syms:
                        sector = sec
                        break
                if not sector:
                    continue
                if sector not in sector_gains:
                    sector_gains[sector] = []
                sector_gains[sector].append(percent_change)

            # Calculate average gain per sector
            sector_avg_gains = {sector: sum(gains) / len(gains) for sector, gains in sector_gains.items() if gains}
            top_sectors = sorted(sector_avg_gains, key=sector_avg_gains.get, reverse=True)[:2]
            logger.info(f"Top gaining sectors: {top_sectors}")
            return top_sectors
        except Exception as e:
            logger.error(f"Error calculating top gaining sectors: {str(e)}")
            return []

    def get_stock_list(self):
        top_sectors = self.get_top_gaining_sectors()
        if not top_sectors:
            return []
        # Get symbols from top two sectors
        symbols = []
        for sector in top_sectors:
            symbols.extend(self.sector_mapping.get(sector, []))
        return symbols

    def get_stock_data(self, price_range):
        try:
            symbols = self.get_stock_list()
            if not symbols:
                logger.error("No stocks available from top gaining sectors")
                return {"error": "No stocks available from top gaining sectors. Please try again later."}

            if price_range == 'None':
                price_min, price_max = 0, float('inf')
            elif price_range.endswith('+'):
                price_min, price_max = int(price_range[:-1]), float('inf')
            else:
                price_min, max_price = map(int, price_range.split('-'))
                if price_min < 0 or max_price <= price_min:
                    logger.error(f"Invalid price range: {price_range}")
                    return {"error": f"Invalid price range: {price_range}. Ensure minimum is non-negative and maximum is greater than minimum."}

            if not self.kite.access_token:
                logger.warning("Kite API not authenticated; returning empty stock data")
                return []

            # Batch symbols to avoid 414 Request-URI Too Large
            batch_size = 500
            market_data = {}
            for i in range(0, len(symbols), batch_size):
                batch = [f'NSE:{symbol}' for symbol in symbols[i:i + batch_size]]
                logger.info(f"Querying Kite API for {len(batch)} instruments in batch {i//batch_size + 1}")
                try:
                    market_data.update(self.kite.quote(batch))
                except requests.exceptions.Timeout:
                    logger.error("Kite API request timed out after 15 seconds")
                    return {"error": "Kite API request timed out. Please try again later."}
                except requests.exceptions.ConnectionError as conn_err:
                    logger.error(f"Kite API network error: {str(conn_err)}")
                    return {"error": "Network error connecting to Kite API. Please check your connection."}
                except Exception as e:
                    logger.error(f"Error fetching quotes for batch {i//batch_size + 1}: {str(e)}")
                    return {"error": f"Failed to fetch stock data: {str(e)}"}

            filtered_data = []
            all_prices = []
            for symbol in symbols:
                quote = market_data.get(f'NSE:{symbol}', {})
                if not quote or 'last_price' not in quote:
                    logger.warning(f"No valid quote data for {symbol}")
                    continue
                price = quote.get('last_price', 0)
                all_prices.append((symbol, price))
                if price_range == 'None' or price_min <= price <= price_max:
                    filtered_data.append({
                        'name': quote.get('name', symbol),
                        'symbol': f"{symbol}.NS",
                        'price': price,
                        'volume': quote.get('volume', 0),
                        'change': quote.get('price_change', 0)
                    })
            if not filtered_data:
                available_ranges = sorted(set([f"{int(price // 100 * 100)}-{int((price // 100 + 1) * 100)}" for _, price in all_prices]))
                min_price = min([price for _, price in all_prices], default=0)
                error_msg = (
                    f"No stocks found for price range {price_range} INR in top gaining sectors. "
                    f"Stocks typically trade above {int(min_price)} INR. "
                    f"Try these ranges: {', '.join(available_ranges[:5])} or select '1000+' or 'None'."
                )
                logger.warning(error_msg)
                return {"error": error_msg}
            logger.info(f"Retrieved stock data: {filtered_data}")
            return filtered_data
        except Exception as e:
            logger.error(f"Error fetching stock data: {str(e)}")
            return {"error": f"Failed to fetch stock data: {str(e)}"}

service = StockRecommendationService(kite)

@app.route('/', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def home():
    if not kite.access_token:
        login_url = kite.login_url()
        logger.info(f"Redirecting to Zerodha login: {login_url}")
        return redirect(login_url)

    form = RecommendationForm()
    stocks = None
    request_id = str(uuid4())
    messages = []

    if form.validate_on_submit():
        price_range = form.price_range.data
        time_horizon = form.time_horizon.data
        risk_level = form.risk_level.data

        range_str = parse_price_range(price_range)
        time_str = parse_time_horizon(time_horizon)
        risk_str = parse_risk_level(risk_level)

        cache_key = f"recommendations_{price_range.lower()}_{time_horizon.lower()}_{risk_level.lower()}"
        cached_result = cache.get(cache_key)
        if cached_result:
            stocks = cached_result
            logger.info(f"Using cached recommendations for {cache_key}")
        else:
            stock_data = service.get_stock_data(price_range)
            if isinstance(stock_data, dict) and 'error' in stock_data:
                flash(stock_data['error'], 'error')
                messages.append(stock_data['error'])
                stocks = []
            else:
                prompt = build_prompt(range_str, time_str, risk_str, stock_data)
                try:
                    stocks = get_recommendations_from_api(prompt, cache_key)
                except Exception as e:
                    logger.error(f"Error: {str(e)}")
                    flash(f"Error: {str(e)}", 'error')
                    messages.append(f"Error: {str(e)}")
                    stocks = cache.get(cache_key) or []
                    if not stocks:
                        flash("No recommendations available due to API failure. Try again later.", 'error')
                        messages.append("No recommendations available due to API failure. Try again later.")

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'stocks': stocks,
                'messages': messages,
                'request_id': request_id
            })
    elif form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                error_msg = f"Error in {form[field].label.text}: {error}"
                flash(error_msg, 'error')
                messages.append(error_msg)

    return render_template('index.html', form=form, stocks=stocks, request_id=request_id)

@app.route('/callback')
def callback():
    request_token = request.args.get('request_token')
    logger.info(f"Received request_token: {request_token}")
    if request_token:
        try:
            data = kite.generate_session(request_token, api_secret=KITE_API_SECRET)
            kite.set_access_token(data['access_token'])
            logger.info("Successfully authenticated with Zerodha")
            flash('Successfully authenticated with Zerodha.', 'success')
            return redirect('/')
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            flash(f'Authentication failed: {str(e)}', 'error')
    else:
        logger.error("No request_token received in callback")
        flash('Authentication failed: No request token provided.', 'error')
    return redirect('/')

def parse_price_range(price_range):
    if price_range == 'None':
        return "any price"
    elif price_range.endswith('+'):
        min_price = int(price_range[:-1])
        return f"above {min_price} INR"
    else:
        min_price, max_price = map(int, price_range.split('-'))
        return f"between {min_price} and {max_price} INR"

def parse_time_horizon(time_horizon):
    if time_horizon == 'None':
        return "any time horizon"
    return time_horizon

def parse_risk_level(risk_level):
    if risk_level == 'None':
        return "any risk level"
    return f"{risk_level} risk level"

def build_prompt(range_str, time_str, risk_str, stock_data):
    optimized_stock_data = [
        {'symbol': stock['symbol'], 'price': stock['price']}
        for stock in stock_data
    ]
    base = (
        "Recommend up to 5 stocks from the Indian stock market (NSE) "
        f"from top-performing sectors trading {range_str} "
        f"with high potential for {time_str} growth (short-term: 3-6 months, medium-term: 1-2 years, long-term: 3-5 years) "
        f"and {risk_str} (low: beta < 0.8, medium: beta 0.8-1.2, high: beta > 1.2). "
        f"Stock Data: {json.dumps(optimized_stock_data, indent=2)}. "
        "Ensure symbols end with .NS. Provide brief reasons (max 100 characters). "
        "Return valid JSON: {'stocks': [{'name': 'Full Name', 'symbol': 'SYMBOL.NS', 'reason': 'brief reason'}]}."
    )
    logger.info(f"Prompt size: {len(base)} characters")
    return base

def get_recommendations_from_api(prompt, cache_key):
    api_url = 'https://api.x.ai/v1/chat/completions'
    headers = {
        'Authorization': f'Bearer {GROK_API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        'model': 'grok-3-mini',
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': 5000,
        'temperature': 0.7,
        'response_format': {'type': 'json_object'}
    }
    try:
        response = session.post(api_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        api_data = response.json()
        content = api_data['choices'][0]['message']['content']
        logger.debug(f"API response: {response.text}")
        logger.info(f"Raw API content: {content}")
        stocks = parse_api_response(content)
        cache.set(cache_key, stocks, timeout=1800)
        return stocks
    except requests.exceptions.Timeout:
        logger.error("API request timed out after 30 seconds")
        raise RuntimeError("API request timed out. Please try again later.")
    except requests.exceptions.ConnectionError as conn_err:
        logger.error(f"API network error: {str(conn_err)}")
        raise RuntimeError("Network error connecting to API. Please check your connection.")
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"API HTTP Error: {str(http_err)}")
        if http_err.response.status_code == 429:
            raise RuntimeError("API rate limit exceeded. Please try again later.")
        elif http_err.response.status_code == 403:
            raise RuntimeError("API authentication failed. Please check your GROK_API_KEY.")
        elif http_err.response.status_code == 401:
            raise RuntimeError("API key is invalid or expired. Please verify your GROK_API_KEY.")
        else:
            raise RuntimeError(f"API Error ({http_err.response.status_code}): {str(http_err)}")
    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        raise ValueError(f"Error fetching recommendations: {str(e)}")

def parse_api_response(content):
    try:
        if len(content) < 10:
            raise ValueError("API response too short or empty")
        if not content.strip().endswith('}'):
            logger.warning("API response appears to be truncated, attempting to fix...")
            if content.count('{') > content.count('}'):
                content = content + '"}]}'
            elif content.count('[') > content.count(']'):
                content = content + '"]}'
            elif not content.strip().endswith('}'):
                content = content + '}'
        
        json_result = json.loads(content)
        if 'stocks' not in json_result or not isinstance(json_result['stocks'], list):
            raise ValueError("Invalid JSON structure: 'stocks' key missing or not a list")
        stocks = json_result.get('stocks', [])
        
        valid_stocks = []
        for stock in stocks:
            if all(key in stock for key in ['name', 'symbol', 'reason']):
                if stock['name'] and stock['symbol'] and stock['reason']:
                    valid_stocks.append(stock)
                else:
                    logger.warning(f"Skipping incomplete stock entry: {stock}")
            else:
                logger.warning(f"Skipping invalid stock entry: {stock}")
        
        if not valid_stocks:
            raise ValueError("No valid stock recommendations found in API response")
        
        return valid_stocks
    except json.JSONDecodeError as json_err:
        logger.error(f"JSON Parse Error: {str(json_err)}")
        logger.error(f"Problematic content: {content}")
        raise ValueError(f"Error parsing recommendations: Invalid JSON format - {str(json_err)}")
    except Exception as e:
        logger.error(f"JSON Parse Error: {str(e)}")
        raise ValueError(f"Error parsing recommendations: {str(e)}")

if __name__ == '__main__':
    # Get port from environment variable for deployment platforms
    port = int(os.environ.get('PORT', 5003))
    # Run in debug mode only if not in production
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)