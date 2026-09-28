"""Offline structural, citation-identity and independent numerical reconciliation."""
import csv,hashlib,json,math,re,sys
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'prototypes/ledger_router'))
from shared.accounting import Usage,Rates,tokens
from core import Router,model_answer,gold
required=['README.md','references.bib','data/literature.csv']+[f'docs/{x}' for x in ['00-scope-and-definitions.md','01-tooling-audit-and-use-ledger.md','02-search-protocol.md','03-literature-review.md','04-evidence-matrix.md','05-literature-gaps.md','06-project-portfolio.md','07-selected-projects.md','08-implementation-roadmap.md','09-experiments-and-results.md','10-risks-limitations-and-open-questions.md','11-work-log.md']]
for path in required:assert (ROOT/path).stat().st_size>50,path
lit=list(csv.DictReader(open(ROOT/'data/literature.csv')));assert len({r['identifier'] for r in lit})==len(lit)
bib=(ROOT/'references.bib').read_text()
for r in lit:
 assert r['title']!='unverified' and r['authors']!='unverified',r['key']
 assert '@misc{'+r['key']+',' in bib and r['url'] in bib,r['key']
 assert (ROOT/'data/raw'/f"{r['key']}.html").exists(),r['key']
 assert 'Verifying your browser' not in (ROOT/'data/raw'/f"{r['key']}.html").read_text(),r['key']
# Reconcile every router charge and actual serialized fixture tokens.
base=ROOT/'prototypes/ledger_router/results';cfg=json.loads((base/'summary.json').read_text())['pricing']
work={q['id']:q for q in map(json.loads,(base/'workload.jsonl').read_text().splitlines())}
groups=defaultdict(list);router=Router(cfg,{},'full');rcount=0
for line in (base/'requests.jsonl').read_text().splitlines():
 r=json.loads(line);q=work[r['id']];assert r['correct']==(r['answer']==gold(q))
 total=r['verification_cost_usd']
 for c in r['calls']:
  u=Usage(**{k:c[k] for k in Usage.__dataclass_fields__});cost=Rates(**cfg['models'][c['model']]).cost(u)
  assert math.isclose(cost,c['cost_usd'],abs_tol=1e-12)
  assert u.input_tokens==len(tokens(router.prompt(q)))
  expected=0 if c['error'] else len(tokens(json.dumps(model_answer(c['model'],q),sort_keys=True)))
  assert u.output_tokens==expected
  total+=cost
 assert math.isclose(total,r['cost_usd'],abs_tol=1e-12)
 groups[(r['scenario'],r['policy'])].append(r);rcount+=1
for s in json.loads((base/'summary.json').read_text())['summary']:
 rs=groups[(s['scenario'],s['policy'])];assert len(rs)==s['n'];assert sum(r['correct'] for r in rs)==s['successes']
 assert math.isclose(sum(r['cost_usd'] for r in rs),s['cost_usd'],abs_tol=1e-10)
 assert s['model_calls']==sum(len(r['calls']) for r in rs)
 if s['scenario']=='cold':assert s['cached_tokens']==0
# Load policy-blind context reader without importing its accounting module.
import importlib.util
spec=importlib.util.spec_from_file_location('context_reader',ROOT/'prototypes/context_guard/reader.py');reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
base=ROOT/'prototypes/context_guard/results';cr=json.loads((base/'results.json').read_text());cg=defaultdict(list);states={};ccount=0
for line in (base/'requests.jsonl').read_text().splitlines():
 r=json.loads(line);key=(r['scenario'],r['policy'],r['budget'],r['sweep']);ids=tokens(r['request']);out=tokens(r['output']);assert len(ids)==r['serialized_input_tokens']
 assert r['success']==(r['executed'] and r['actual']==r['gold'])
 if r['executed']:assert reader.answer(r['request'])==r['actual']
 if r['submitted']:
  assert len(ids)+cr['config']['output_reserve']<=r['budget']
  assert r['input_tokens']==len(ids) and r['output_tokens']==len(out)
  previous,at=states.get(key,([],float('-inf')));n=0
  if r['now']-at<=cr['config']['cache']['ttl']:
   for a,b in zip(previous,ids):
    if a!=b:break
    n+=1
  n=n//cr['config']['cache']['block']*cr['config']['cache']['block'];n=n if n>=cr['config']['cache']['minimum'] else 0
  assert n==r['cached_tokens'];states[key]=(ids,r['now'])
 else:assert r['input_tokens']==r['output_tokens']==r['cached_tokens']==0
 rates=cr['config']['rates'];cost=((r['input_tokens']-r['cached_tokens'])*rates['input']+r['cached_tokens']*rates['cache_read']+r['output_tokens']*rates['output'])/1e6
 assert math.isclose(cost,r['cost_usd'],abs_tol=1e-12)
 cg[key].append(r);ccount+=1
for s in cr['runs']:
 rs=cg[(s['scenario'],s['policy'],s['budget'],s['sweep'])]
 assert len(rs)==s['requests'] and sum(r['success'] for r in rs)==s['successes']
 assert math.isclose(sum(r['cost_usd'] for r in rs),s['cost_usd'],abs_tol=1e-12)
# Validate project-local Markdown destinations, ignoring anchors and external URLs.
bad=[]
for p in list((ROOT/'docs').glob('*.md'))+[ROOT/'README.md']+list((ROOT/'prototypes').glob('*/README.md')):
 expected_columns=None
 for line in p.read_text().splitlines():
  if line.startswith('|'):
   columns=len(line.split('|'))-2
   if expected_columns is None:expected_columns=columns
   assert columns==expected_columns,(p,line)
  else:expected_columns=None
 for dest in re.findall(r'\]\(([^)]+)\)',p.read_text()):
  if dest.startswith(('https://','http://','#')):continue
  dest=dest.split('#')[0].strip('<>')
  if dest and (p.parent/dest).resolve() != ROOT/'results/verification.json' and not (p.parent/dest).exists():bad.append([str(p),dest])
assert not bad,bad
result={'passed':True,'primary_works':len(lit),'required_nonempty_files':len(required),'router_request_ledgers_reconciled':rcount,'router_policy_summaries':len(groups),'context_request_ledgers_reconciled':ccount,'context_trajectory_summaries':len(cg),'local_markdown_links':'passed','sources_directory_entries':len(list((ROOT/'sources').iterdir()))}
(ROOT/'results/verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
