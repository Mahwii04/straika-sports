from datetime import datetime, timedelta
from functools import wraps
from flask import current_app

def api_limit_guard(f):
    """Decorator to protect API call functions from exceeding limits"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not rate_limit_check():
            current_app.logger.warning("API call blocked - limit reached")
            return None
        return f(*args, **kwargs)
    return decorated_function

def rate_limit_check():
    """Check if we're under daily API call limit"""
    api_config = current_app.config.get('API_CONFIG', {}).get('FOOTBALL_DATA_API', {})
    max_calls = api_config.get('MAX_CALLS_PER_DAY', 95)
    
    # In a real implementation, you'd want to persist this counter
    # between app restarts (e.g., in database or Redis)
    today = datetime.now().date().isoformat()
    call_count = getattr(current_app, '_api_call_count', {}).get(today, 0)
    
    return call_count < max_calls

def log_api_call():
    """Track API calls to stay under limits"""
    today = datetime.now().date().isoformat()
    
    if not hasattr(current_app, '_api_call_count'):
        current_app._api_call_count = {}
    
    current_app._api_call_count[today] = current_app._api_call_count.get(today, 0) + 1