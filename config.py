import os

class Config:
    KITE_API_KEY = os.environ.get('KITE_API_KEY')
    KITE_API_SECRET = os.environ.get('KITE_API_SECRET')
    GROK_API_KEY = os.environ.get('GROK_API_KEY')
    FLASK_SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'your-secret-key')