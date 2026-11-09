from ast import Nonlocal
import collections
from csv import Error
import functools
import time
from typing import Iterator

def suppress_and_trip(max_consecutive_errors: int):
    def decorator(func):
        consecutive_errors = 0
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal consecutive_errors
            try:
                result = func(*args, **kwargs)
                consecutive_errors = 0 
                return result
            except Exception:
                consecutive_errors += 1
                if consecutive_errors >= max_consecutive_errors:
                    raise Error   
                return None                
        return wrapper
    return decorator

class StreamSession:
    def __init__(self, stream):
        self.stream = stream
        self.elapsed_time = 0.0

    def __enter__ (self):
        self.stream.open()
        self.start_time = time.perf_counter()
        return self.stream
    
    def __exit__ (self, exc_type, exc_val, exc_tb):
        self.stream.close()
        self.elapsed_time = time.perf_counter() - self.start_time
        if exc_type == EOFError:
                return True
        
@suppress_and_trip(max_consecutive_errors=3)
def parse_tick(line: str) -> tuple[str, float, int]:
    parts = line.strip().split(",")
    if len(parts) != 3:
        raise ValueError(f"Malformed line: {line}")
    symbol, price_str, vol_str = parts
    price, volume = float(price_str), int(vol_str)
    if price <= 0 or volume <= 0:
        raise ValueError(f"Non-positive trade values: {line}")
    return symbol, price, volume

def rolling_vwap(stream: Iterable[str], window_size: int) -> Iterator[tuple[str, float]]:
    # TODO: Implement O(1) time per tick generator pipeline
    symbols = collections.defaultdict(collections.deque)
    tot_vol = collections.defaultdict(int)
    tot_price = collections.defaultdict(int)
    for tick in stream:
        parsed = parse_tick(tick)
        if parsed is None:
            continue
        symbol, price, volume = parsed
        if len(symbols[symbol]) == window_size:
            removed = symbols[symbol].popleft()
            tot_price[symbol] -= removed[0]
            tot_vol[symbol] -= removed[0]*removed[1]
        symbols[symbol].append((price,volume))
        tot_price[symbol] += price
        tot_vol[symbol] += price*volume
        vwap = tot_price[symbol] / tot_vol[symbol]
        yield (symbol, vwap)