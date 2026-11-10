import collections
from copy import deepcopy
import functools
import time
from typing import Iterator

class RateLimitExceeded(Exception):
    pass

def rate_limit(max_calls: int, time_window_seconds: float):
    def decorator(func):
        calls = collections.deque()
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            while calls and calls[0] < (time.perf_counter() - time_window_seconds):
                calls.popleft()
            if len(calls) >= max_calls:
                raise RateLimitExceeded
            else:
                calls.append(time.perf_counter())
            return func(*args, **kwargs)
        return wrapper
    return decorator

def merge_sorted_streams(stream_a: Iterator[tuple[int, float]], stream_b: Iterator[tuple[int, float]]) -> Iterator[tuple[int, float]]:
    while (a := next(stream_a, None)) is not None and (b := next(stream_b, None)) is not None:
        if a[0] <= b[0]:
            yield a
        else:
            yield b
    while (a := next(stream_a, None)) is not None:
        yield a
    while (b := next(stream_b, None)) is not None:
        yield b

class StateRollback:
    def __init__(self, target_dict: dict):
        self.target_dict = target_dict
        self.store_dict = deepcopy(self.target_dict)
    
    def __enter__(self):
        return self.target_dict
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.target_dict = self.store_dict
