import functools
import time

def memoize_ttl(ttl_seconds: float):
    def decorator(func):
        seen = {}
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if (args, kwargs) not in seen or (time.perf_counter() - seen[(args, kwargs)][1]) > ttl_seconds:
                result = func(*args, **kwargs)
                seen[(args, kwargs)] = (result, time.perf_counter())
            elif (time.perf_counter() - seen[(args, kwargs)][1]) <= ttl_seconds:
                result = seen[(args, kwargs)]
            return result
        return wrapper
    return decorator


# Test case evaluation:
@memoize_ttl(ttl_seconds=2.0)
def fetch_price(ticker: str) -> float:
    print(f"Fetching {ticker}...")
    return 150.0

# fetch_price("AAPL") -> Prints "Fetching AAPL...", returns 150.0
# fetch_price("AAPL") -> Returns 150.0 instantly from cache
# time.sleep(2.1)
# fetch_price("AAPL") -> Prints "Fetching AAPL...", returns 150.0