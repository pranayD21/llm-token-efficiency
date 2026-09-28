"""A deterministic replay router; simulated engines are not claims about any LLM."""
import hashlib,json,math,re,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from shared.accounting import PrefixCache,Rates,Usage,tokens
PREFIX='Apply the current tenant policy. Return a JSON decision and cite the policy version. Never mix tenant records.\n'*100

def gold(q):
    return {'approved':q['amount']<=q['limit'] and not q['blocked'], 'version':q['version']}

def model_answer(model,q):
    if model.startswith('strong'):
        return {'approved':False if q['blocked'] else q['amount']<=q['limit'],'version':q['version']}
    # Deliberately limited local model: understands standard policy, ignores exceptions.
    answer={'approved':q['amount']<=q['limit'],'version':q['version']}
    if q['wording']=='shifted' or q['amount']==419: answer['approved']=not answer['approved']
    return answer

def verify(q,answer):
    # Does not solve approval itself. Enforces version/schema and abstains on exceptional inputs.
    return set(answer)=={'approved','version'} and type(answer['approved']) is bool and answer['version']==q['version'] and not q['blocked'] and q['wording']!='shifted'

def bucket(q): return 'exception' if q['blocked'] else 'standard'
def wilson_lower(success,n,z=1.96):
    if not n:return 0
    p=success/n
    return (p+z*z/(2*n)-z*math.sqrt(p*(1-p)/n+z*z/(4*n*n)))/(1+z*z/n)

def calibrate(rows):
    out={}
    for q in rows:
        k=bucket(q); state=out.setdefault(k,{'successes':0,'n':0,'rejections':0})
        answer=model_answer('small',q);state['successes']+=answer==gold(q);state['n']+=1
        state['rejections']+=not verify(q,answer)
    return {k:{**v,'lower95':wilson_lower(v['successes'],v['n']),'point':v['successes']/v['n'],'reject_rate':v['rejections']/v['n']} for k,v in out.items()}

def signature(q):
    return tuple(q[k] for k in ['tenant','version','amount','limit','blocked','wording'])

class Router:
    def __init__(self,config,calibration,policy):
        self.cfg=config; self.cal=calibration; self.policy=policy
        self.rates={k:Rates(**v) for k,v in config['models'].items()}
        self.prefix=PrefixCache(config['minimum_prefix'],config['cache_block'],config['prefix_ttl'])
        self.responses={};self.bad=0;self.small_seen=0
    def prompt(self,q): return PREFIX+json.dumps({k:v for k,v in q.items() if k not in ['id','time','scenario']},sort_keys=True)
    def key(self,model,q): return (q['tenant'],q['version'],model)
    def estimate(self,model,q,now,aware=None):
        if aware is None: aware=self.policy!='cache_blind_routing'
        ids=tokens(self.prompt(q));read=self.prefix.peek(self.key(model,q),ids,now) if aware else 0
        # All uncached input is charged at write rate in this illustrative explicit-cache mode.
        return self.rates[model].cost(Usage(len(ids),15,read,len(ids)-read))
    def _attempt(self,model,q,now,fail=False):
        prompt=self.prompt(q);ids=tokens(prompt);key=self.key(model,q)
        read=self.prefix.peek(key,ids,now);a=model_answer(model,q)
        usage=Usage(len(ids),0 if fail else len(tokens(json.dumps(a,sort_keys=True))),read,len(ids)-read)
        self.prefix.put(key,ids,now)
        return a,{'model':model,'error':fail,**usage.__dict__,'cost_usd':self.rates[model].cost(usage),'simulated_latency_ms':35 if model=='small' else 250}
    def call(self,model,q,now):
        calls=[]
        if q.get('transient',False):
            _,failed=self._attempt(model,q,now,fail=True);calls.append(failed)
        answer,success=self._attempt(model,q,now);calls.append(success)
        return answer,calls
    def run(self,q):
        start=time.perf_counter();now=q['time'];calls=[];extra=0;hit=False;fallback=False;verification_calls=0
        p=self.policy;k=signature(q)
        cache_enabled=p in ['full','no_verifier','cache_blind_routing','unsafe_cache','no_drift_guard','strong_a_cached','strong_b_cached']
        if p=='unsafe_cache': k=(q['amount'],) # Deliberate unsafe similarity proxy ablation.
        entry=self.responses.get(k)
        if p=='exact_local':
            a={'approved':not(q['blocked'] or q['amount']>q['limit']),'version':q['version']}
        elif cache_enabled and entry and now-entry[1]<self.cfg['response_ttl']:
            a=entry[0];hit=True
        else:
            strong=min(['strong_a','strong_b'],key=lambda m:self.estimate(m,q,now))
            lower=self.cal.get(bucket(q),{}).get('lower95',0)
            reject_rate=self.cal.get(bucket(q),{}).get('reject_rate',1)
            expected=self.estimate('small',q,now)+self.cfg['verifier_usd']+reject_rate*self.estimate(strong,q,now)
            drifted=self.small_seen>=10 and self.bad/self.small_seen>0.10
            choose_small=lower>=self.cfg['quality_target'] and expected<self.estimate(strong,q,now) and (not drifted or p=='no_drift_guard')
            if p in ['strong','strong_a_cached']:model='strong_a'
            elif p=='strong_b_cached':model='strong_b'
            elif p=='cheap':model='small'
            elif p=='cascade':model='small'
            else:model='small' if choose_small else strong
            a,c=self.call(model,q,now);calls.extend(c)
            if model=='small' and p not in ['cheap','no_verifier']:
                verification_calls+=1;extra+=self.cfg['verifier_usd'];ok=verify(q,a)
                self.small_seen+=1;self.bad+=not ok
                if not ok:
                    fallback=True;a,c=self.call(strong,q,now);calls.extend(c)
            if cache_enabled:self.responses[k]=(a,now)
        return {'id':q['id'],'scenario':q['scenario'],'policy':p,'correct':a==gold(q),'answer':a,'response_hit':hit,'fallback':fallback,'verification_calls':verification_calls,'verification_cost_usd':extra,'cost_usd':sum(c['cost_usd'] for c in calls)+extra,'calls':calls,'local_overhead_ms':(time.perf_counter()-start)*1000}
