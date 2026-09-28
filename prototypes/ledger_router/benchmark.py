import argparse,json,random,statistics
from pathlib import Path
from core import Router,calibrate
HERE=Path(__file__).resolve().parent

def make_workload(seed=17):
    rng=random.Random(seed); train=[];test=[]
    for i in range(600):
        train.append(dict(id=f'train-{i}',tenant='train',version=1,amount=rng.randint(1,1000),limit=500,blocked=i%3==0,wording='normal',time=i,scenario='calibration'))
    for scenario in ['stationary','drift','tenant_version_attack','cold','cache_affinity','wording_drift','transient_failure']:
        for i in range(240):
            # Repeat within a tenant/version; variation and explicit attacks are separate.
            j=i%60; tenant='A' if scenario!='tenant_version_attack' or (i//60)%2==0 else 'B'
            q=dict(id=f'{scenario}-{i}',tenant=tenant,version=1 if i<120 else 2,amount=100+j*11,limit=500 if tenant=='A' else 250,blocked=j%9==0,wording='shifted' if scenario in ['drift','wording_drift'] and i>=120 else 'normal',time=i*(max(120,300)+1 if scenario=='cold' else 1),scenario=scenario)
            if scenario=='cache_affinity': q.update(blocked=True,version=1)
            if scenario=='wording_drift': q.update(version=1)
            if scenario=='transient_failure': q.update(transient=i%17==0)
            test.append(q)
    return train,test

def summarize(rows):
    n=len(rows);success=sum(r['correct'] for r in rows);calls=[c for r in rows for c in r['calls']]
    return dict(n=n,successes=success,accuracy=success/n,cost_usd=sum(r['cost_usd'] for r in rows),cost_per_success_usd=sum(r['cost_usd'] for r in rows)/success if success else None,cost_per_request_usd=sum(r['cost_usd'] for r in rows)/n,model_calls=len(calls),fallback_calls=sum(r['fallback'] for r in rows),retry_calls=sum(c.get('error',False) for c in calls),verification_calls=sum(r['verification_calls'] for r in rows),response_hit_rate=sum(r['response_hit'] for r in rows)/n,input_tokens=sum(c['input_tokens'] for c in calls),output_tokens=sum(c['output_tokens'] for c in calls),cached_tokens=sum(c['cached_tokens'] for c in calls),cache_write_tokens=sum(c['cache_write_tokens'] for c in calls),reasoning_tokens=0,simulated_model_latency_ms=sum(c['simulated_latency_ms'] for c in calls),local_overhead_p50_ms=statistics.median(r['local_overhead_ms'] for r in rows))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=HERE/'results');args=ap.parse_args();args.output.mkdir(exist_ok=True)
    cfg=json.loads((HERE/'config.json').read_text());train,test=make_workload(cfg['seed']);cal=calibrate(train)
    (HERE/'sample.jsonl').write_text('\n'.join(json.dumps(q) for q in test[:12])+'\n')
    (args.output/'workload.jsonl').write_text('\n'.join(json.dumps(q) for q in test)+'\n')
    all_rows=[];summary=[]
    for scenario in sorted({q['scenario'] for q in test}):
        for p in ['strong','strong_a_cached','strong_b_cached','cheap','cascade','full','no_response_cache','no_verifier','cache_blind_routing','no_drift_guard','unsafe_cache','exact_local']:
            router=Router(cfg,cal,p)
            selected=[q for q in test if q['scenario']==scenario]
            warmup=[]
            if scenario=='cache_affinity' and p!='exact_local':
                _,warmup=router.call('strong_a',selected[0],-1)
                for c in warmup:c['setup']=True
            rows=[router.run(q) for q in selected]
            if warmup:
                rows[0]['calls']=warmup+rows[0]['calls'];rows[0]['cost_usd']+=sum(c['cost_usd'] for c in warmup)
            all_rows+=rows
            summary.append({'scenario':scenario,'policy':p,**summarize(rows)})
    (args.output/'requests.jsonl').write_text('\n'.join(json.dumps(r) for r in all_rows)+'\n')
    (args.output/'summary.json').write_text(json.dumps({'mode':'deterministic simulation; no API results','tokenizer':'tiktoken 0.14.0/cl100k_base','pricing':cfg,'calibration':cal,'summary':summary},indent=2))
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
