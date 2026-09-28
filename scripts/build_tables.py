import json,csv,platform,subprocess,sys
from pathlib import Path
rows=json.loads(Path('data/literature.json').read_text())
for r in rows:
 for f in ['input_tokens','output_tokens','cached_tokens','monetary_cost','latency','energy_compute']:r[f]='not reported'
 r['quality_metric']='see workload-specific source result'
metrics={
 'llmlingua':{'input_tokens':'up to 20x compression'},
 'llmlingua2':{'input_tokens':'2-5x compression','latency':'1.6-2.9x end-to-end speedup'},
 'recomp':{'input_tokens':'as low as 6% retained'},
 'acon':{'input_tokens':'26-54% peak reduction','monetary_cost':'history compression can increase cost'},
 'paritok':{'input_tokens':'25.7% retained','quality_metric':'86.5% retained single-shot solve quality'},
 'cacheblend':{'latency':'2.2-3.3x TTFT; 2.8-5x throughput'},
 'snell':{'energy_compute':'>4x test-time compute efficiency','quality_metric':'MATH accuracy'},
 'selfbudgeter':{'output_tokens':'5327.12 -> 2326.85','quality_metric':'MATH500 74.93% -> 78.47%; AIME25 loss'},
 'estar':{'output_tokens':'4799 -> 1290 reasoning','quality_metric':'74.9% -> 74.2%'},
 's1':{'quality_metric':'AIME24 50% -> 57% with longer budget'},
 'chainofdraft':{'output_tokens':'205.1 -> 43.9','latency':'4.2s -> 1.0s','quality_metric':'GSM8K 95.4% -> 91.1%'},
 'speculative':{'latency':'2-3x acceleration','quality_metric':'target sampling distribution preserved'},
 'eagle3':{'latency':'4.40x MT-bench speedup'},
 'distillsteps':{'quality_metric':'ANLI student beats teacher at 80% training data'},
 'deepseekr1':{'quality_metric':'MATH500 94.3% vs 91.6%'},
 'tokens2words':{'input_tokens':'10.5% shorter WikiText sequences','quality_metric':'.522 -> .519 word accuracy'},
 'pagedattention':{'latency':'2-4x throughput at comparable latency'},
 'sarathi':{'latency':'up to 2.6x capacity at SLO'},
 'agentprune':{'input_tokens':'combined communication token reduction 28.1-72.8%; partition unavailable'},
 'coordination':{'output_tokens':'about 42% reduction in specified eight-agent workload'},
 'frugalgpt':{'monetary_cost':'98.3/73.3/59.2% savings by dataset'},
 'routellm':{'monetary_cost':'3.66x cost-saving ratio','quality_metric':'95% GPT-4 MT-Bench quality'},
 'unified':{'quality_metric':'87.24% cost-quality AUC, specified setting'},
 'mixllm':{'monetary_cost':'24.18% GPT-4 cost','quality_metric':'97.25% GPT-4 quality'},
 'moa':{'quality_metric':'AlpacaEval LC win rate 65.1% vs 57.5%'},
 'preble':{'latency':'1.5-14.5x mean latency improvement'},
 'llmbridge':{'monetary_cost':'40% model-selection savings (component test)'},
 'tweakllm':{'monetary_cost':'61% baseline WildChat cost (estimate)'},
 'groundedcache':{'quality_metric':'USR 51.5% -> 1.5%; hit rate 56.5% -> 2%'},
 'cacheroute':{'latency':'176 vs 76 QPS, 3.5s p99 SLO'},
 'agserve':{'monetary_cost':'16.5% GPT-4o cost on ALFWorld','quality_metric':'90 vs 94 quality'},
}
for r in rows:r.update(metrics.get(r['key'],{}))
Path('data/literature.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
with open('data/literature.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
lines=['# Evidence matrix','','39 deduplicated primary research records. Numerical claims are author-reported, not reproduced. NR means **not reported in the inspected evidence**; it is not proof that the full paper omits a measurement. No energy result was extracted. Complexity is a reviewer estimate of integration/training burden. The machine-readable [CSV](../data/literature.csv) contains full titles, authors, identifiers, source types, status, method, workload, limitations and code availability. Publication dates usually reflect the first preprint; version-specific numerical findings are noted in the result field.','','## Comparable dimensions','','| Work | Quality | Input | Output | Cached | Dollars | Latency / capacity | Energy / compute | Complexity |','|---|---|---|---|---|---|---|---|---|']
for r in rows:
 vals=[f"[{r['key']}]({r['url']})"]+[r[k].replace('not reported','NR') for k in ['quality_metric','input_tokens','output_tokens','cached_tokens','monetary_cost','latency','energy_compute','complexity']]
 lines.append('| '+' | '.join(v.replace('|','/') for v in vals)+' |')
lines+=['','## Method, evidence and reproducibility','','| Work / status | Method and evaluation | Limitation / code |','|---|---|---|']
for r in rows:lines.append(f"| [{r['title']}]({r['url']})<br>{r['status']} | {r['method']}. {r['models_datasets_baselines']} | {r['limitations']}. Code: {r['code']} |")
lines+=['','## Interpretation boundaries','','Token reduction, billing reduction, latency improvement and cost shifting can overlap, but the percentages do not multiply. Router quality scores, unsafe-served rates and exact task accuracy have different denominators. Fixed-model baselines should receive the same cache opportunities as routed systems. Preprints and later revisions are not counted as separate studies. Statements of algorithmic optimality or safety are conditional on the paper’s estimator, distribution and threat assumptions.']
Path('docs/04-evidence-matrix.md').write_text('\n'.join(lines)+'\n')
weights=[.2,.2,.1,.1,.1,.1,.1,.05,.05]
portfolio=[('Ledger Router',[4,4,3,4,4,5,5,5,3]),('Context Guard',[4,4,3,5,4,5,5,4,3]),('Semantic cache risk service',[4,3,2,4,4,3,4,5,2]),('Reasoning budget learner',[5,3,4,2,2,3,2,5,2]),('Joint horizon controller',[5,3,4,2,1,2,2,5,1]),('GPU draft/batch optimizer',[2,5,2,2,1,3,2,4,2])]
port=[{'project':n,'scores':s,'weighted':round(sum(w*v for w,v in zip(weights,s)),2)} for n,s in portfolio]
Path('data/portfolio.json').write_text(json.dumps({'weights':weights,'scale':'1-5 favorable','projects':port},indent=2));print(port)
install=json.loads(Path('data/raw/install-report.json').read_text())
Path('requirements-hashed.txt').write_text('\n'.join(x['metadata']['name']+'=='+x['metadata']['version']+' --hash=sha256:'+x['download_info']['archive_info']['hashes']['sha256'] for x in install['install'])+'\n')
env={'python':sys.version,'platform':platform.platform(),'curl':subprocess.check_output(['/usr/bin/curl','--version'],text=True).splitlines()[0],'packages':subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True).splitlines()}
Path('results/environment.json').write_text(json.dumps(env,indent=2))
