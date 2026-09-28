"""Provider-neutral accounting. Reasoning is included in total output, never added twice."""
from dataclasses import dataclass
from decimal import Decimal
import os, math
from pathlib import Path
os.environ.setdefault('TIKTOKEN_CACHE_DIR', str(Path(__file__).resolve().parents[1]/'data/tokenizer-cache'))
import tiktoken

@dataclass(frozen=True)
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    cache_write_tokens: int = 0
    reasoning_tokens: int = 0
    def __post_init__(self):
        vals=list(self.__dict__.values())
        if any(type(x) is not int or x < 0 for x in vals): raise ValueError('Usage must contain nonnegative integers')
        if self.cached_tokens+self.cache_write_tokens>self.input_tokens: raise ValueError('Input categories overlap')
        if self.reasoning_tokens>self.output_tokens: raise ValueError('Reasoning is a subset of total output')

@dataclass(frozen=True)
class Rates:
    input: float
    output: float
    cached: float
    write: float
    def __post_init__(self):
        if any(not math.isfinite(x) or x<0 for x in self.__dict__.values()): raise ValueError('Price must be finite and nonnegative')
    def cost(self,u,storage_usd=0,tool_usd=0,multiplier=1):
        if any(not math.isfinite(x) or x<0 for x in [storage_usd,tool_usd,multiplier]): raise ValueError('Charge must be finite and nonnegative')
        amounts=[(u.input_tokens-u.cached_tokens-u.cache_write_tokens,self.input),(u.output_tokens,self.output),(u.cached_tokens,self.cached),(u.cache_write_tokens,self.write)]
        return float(sum(Decimal(n)*Decimal(str(p)) for n,p in amounts)/Decimal(1_000_000)*Decimal(str(multiplier))+Decimal(str(storage_usd))+Decimal(str(tool_usd)))

def tokens(text,encoding='cl100k_base'):
    return tiktoken.get_encoding(encoding).encode(text,disallowed_special=())

def openai_usage(raw):
    return Usage(raw['input_tokens'],raw['output_tokens'],raw.get('input_tokens_details',{}).get('cached_tokens',0),raw.get('input_tokens_details',{}).get('cache_write_tokens',0),raw.get('output_tokens_details',{}).get('reasoning_tokens',0))

def anthropic_usage(raw):
    read=raw.get('cache_read_input_tokens',0); write=raw.get('cache_creation_input_tokens',0)
    return Usage(raw['input_tokens']+read+write,raw['output_tokens'],read,write,0)

def gemini_usage(raw):
    thinking=raw.get('thoughtsTokenCount',0)
    return Usage(raw['promptTokenCount'],raw.get('candidatesTokenCount',0)+thinking,raw.get('cachedContentTokenCount',0),0,thinking)

class PrefixCache:
    def __init__(self,minimum=1024,block=128,ttl=300):
        self.minimum=minimum; self.block=block; self.ttl=ttl; self.entries={}
    def peek(self,key,ids,now):
        old,at=self.entries.get(key,([],float('-inf')))
        if now-at>=self.ttl: return 0
        n=0
        for a,b in zip(old,ids):
            if a!=b: break
            n+=1
        return n//self.block*self.block if n>=self.minimum else 0
    def put(self,key,ids,now): self.entries[key]=(list(ids),now)
