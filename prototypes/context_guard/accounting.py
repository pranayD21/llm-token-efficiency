"""Illustrative request accounting; no provider API semantics implied."""
import json
import os
from pathlib import Path

SHARED_CACHE = Path(__file__).resolve().parents[2] / 'data' / 'tokenizer-cache'
os.environ.setdefault('TIKTOKEN_CACHE_DIR', str(SHARED_CACHE))
import tiktoken
ENC = tiktoken.get_encoding('cl100k_base')


def dump(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'))


def tokens(text):
    return ENC.encode(text, disallowed_special=())


class Cache:
    """Single previous submitted input, sliding TTL, whole prefix blocks."""
    def __init__(self, config):
        self.config = config
        self.previous = []
        self.at = None
        if config['block'] <= 0 or config['minimum'] < 0 or config['ttl'] < 0:
            raise ValueError('Invalid cache configuration')

    def prefix(self, current, now):
        if self.at is None or now - self.at > self.config['ttl']:
            return 0
        n = 0
        for a, b in zip(self.previous, current):
            if a != b:
                break
            n += 1
        n = n // self.config['block'] * self.config['block']
        return n if n >= self.config['minimum'] else 0

    def estimate(self, current, now, rates):
        cached = self.prefix(current, now)
        return ((len(current) - cached) * rates['input'] + cached * rates['cache_read']) / 1e6

    def bill(self, current, output, now, rates, submitted=True):
        cached = self.prefix(current, now) if submitted else 0
        billed = len(current) if submitted else 0
        out = len(tokens(output)) if submitted else 0
        result = dict(input_tokens=billed, serialized_input_tokens=len(current),
                      cached_tokens=cached, uncached_tokens=billed-cached, output_tokens=out,
                      cost_usd=((billed-cached)*rates['input'] + cached*rates['cache_read']
                                + out*rates['output'])/1e6)
        if submitted:
            self.previous, self.at = list(current), now
        return result
