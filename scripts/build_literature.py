"""Curated evidence annotations. Metadata comes from downloaded primary-source pages."""
import csv,json,re
from html.parser import HTMLParser
from pathlib import Path
class Meta(HTMLParser):
 def __init__(self):super().__init__();self.meta={}
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='meta' and 'name' in a:self.meta.setdefault(a['name'],[]).append(a.get('content',''))
# key | id | category | method | workload/baseline | observed source result | caveat | code
SPEC='''llmlingua|acl:2023.emnlp-main.825|context|Budgeted token pruning with distribution alignment|GSM8K; BBH; ShareGPT; Arxiv-March23|Up to 20x prompt compression with little reported performance loss|Best-case compression; compression model overhead|https://github.com/microsoft/LLMLingua
llmlingua2|acl:2024.findings-acl.57|context|Distilled bidirectional token classifier|MeetingBank; LongBench; ZeroScrolls; GSM8K; BBH|2-5x compression; 1.6-2.9x end-to-end speedup|Dataset averages do not establish rare-detail retention|https://github.com/microsoft/LLMLingua
recomp|2310.04408|retrieval|Extractive or abstractive selective augmentation|Language modeling; NQ; TriviaQA; HotpotQA; uncompressed RALM|Compressed context as low as 6% of original|Training and retrieval costs shift upstream; no universal ratio|not verified
lostmiddle|2307.03172|context|Position-sensitive evaluation|Multi-document QA and key-value retrieval|Accuracy depends on relevant information position|Diagnostic study; not a cost-reduction intervention|not verified
meancache|2403.02694|semantic cache|User-local cache; federated similarity; context chains|Semantic hit/miss and contextual query tests|About 17% higher F-score and 20% higher precision as reported|Relative-versus-point interpretation not resolved; privacy claim is not a complete threat audit|not verified
lacache|2608.01718|semantic cache|Check query and initial decoded-token cache matches|Diverse LLMs; attack and retrieval evaluation|Security and relevance improvement reported; numeric claim not extracted|Formal guarantees depend on assumptions; preprint|not verified
onlinecache|2508.07675|semantic cache|Offline optimization and online cache eviction|Synthetic query and cost distributions|Theoretical guarantees and synthetic benchmark comparison|Already treats mismatch cost and unknown distributions; real trace generalization unestablished|not verified
acon|2510.00615|agent context|Optimize compression guidelines; distill compressor|AppWorld; OfficeBench; multi-objective QA|26-54% peak-token reduction; history compression can increase API cost|Peak tokens are not cumulative billed tokens; cache invalidation and compressor costs|not verified
paritok|2608.24188|agent context|Intent-conditioned extractive 4B LoRA compressor|300 SWE-bench Lite tasks; uncompressed and LLM compressors|25.7% retained context; 86.5% retained single-shot solve quality|Quality loss remains; nonsignificance is not proof of equivalence|author says weights/data/scripts open; URL not verified
cacheblend|2405.16444|KV cache|Partial recomputation of reused non-prefix KV chunks|Three LLMs; four benchmarks; full KV recomputation|2.2-3.3x TTFT improvement; 2.8-5x throughput|Serving compute/latency benefit; no direct API token discount implied|https://github.com/LMCache/LMCache
freshcache|2607.04281|semantic cache|Temporal risk gate for answer/URL/page reuse|8072 base queries; temporal web snapshots|Reported search API savings; hash-based staleness differs from answer errors|Preprint; paraphrases are not independent queries; judge subset|not verified
snell|2408.03314|reasoning|Difficulty-aware search and sequential revisions|PaLM 2-S*; MATH500; best-of-N|More than 4x test-time compute efficiency vs best-of-N|Trained verifiers and domain-specific difficulty; no billed-token claim|not verified
selfbudgeter|2505.11274|reasoning|Learn predicted token budgets with GRPO|R1-Distill-Qwen 1.5B; MATH500; original student|5327.12 to 2326.85 tokens; 74.93% to 78.47% accuracy, v6 Table 1|AIME2025 accuracy instead falls 22.22% to 21.11%|not verified
estar|2602.10004|reasoning|Trajectory classifier plus trained stopping signals|USMLE; JAMA; MATH500; AIME2025|4799 to 1290 reasoning tokens; 74.9% to 74.2% accuracy|Small absolute quality loss; confidence is not correctness|not verified
s1|2501.19393|reasoning|Budget forcing and 1000-example fine-tuning|Qwen2.5-32B; AIME24; no budget intervention|Longer budget increases AIME24 accuracy from 50% to 57%|This example spends more tokens; budget control is not always reduction|https://github.com/simplescaling/s1
chainofdraft|2502.18600|output|Prompt concise intermediate drafts|GPT-4o; GSM8K; CoT baseline|205.1 to 43.9 output tokens; 95.4% to 91.1% accuracy; 4.2s to 1.0s|v1 Table 1 contradicts blanket no-quality-loss interpretation|https://github.com/sileix/chain-of-draft
speculative|2211.17192|inference|Draft and target rejection-corrected sampling|T5-XXL; translation; summarization; autoregressive baseline|2-3x acceleration; target distribution preserved|Output count unchanged; draft work and acceptance rate matter|not verified
eagle3|2503.01840|inference|Feature-fused trained draft model|Llama 3.1 8B; MT-bench; autoregressive decoding|4.40x MT-bench speedup, v1 Table 2|Batch size and hardware matter; no reduction in requested output|https://github.com/SafeAILab/EAGLE
distillsteps|2305.02301|distillation|Train smaller students with teacher rationales|ANLI; T5-770M vs PaLM-540B|Student beats teacher using 80% training data on ANLI|Training and teacher generation must be amortized; task specialization|https://github.com/google-research/distilling-step-by-step
deepseekr1|2501.12948|distillation|Distill generated reasoning into smaller models|Qwen-32B; MATH500; direct RL baseline|94.3% vs 91.6% MATH500, v1 Tables 5-6|Parameter reduction does not establish shorter reasoning|https://github.com/deepseek-ai/DeepSeek-R1
tokens2words|2410.05864|tokenization|Expand model vocabulary with learned representations|Llama2-7B; WikiText-103; original tokenizer|10.5% shorter WikiText sequences; accuracy .522 to .519|Requires model changes; raw perplexities across tokenizers incomparable|https://github.com/schwartz-lab-NLP/Tokens2Words
pagedattention|2309.06180|inference|Paged KV memory and shared state|OPT/LLaMA; ShareGPT/Alpaca; FasterTransformer/Orca|2-4x throughput at comparable latency|Historical baselines; logical tokens need not decrease|https://github.com/vllm-project/vllm
sarathi|2403.02310|scheduling|Chunked prefill with decode scheduling|Mistral-7B on A100; vLLM|Up to 2.6x capacity under latency SLO, v1|Workload and SLO dependent; not per-request token reduction|https://github.com/microsoft/sarathi-serve
agentprune|2410.02506|multi-agent|Prune spatial and temporal message edges|AutoGen/GPTSwarm; reasoning and code workloads|28.1-72.8% token reduction reported|Pruning cost and original graph redundancy determine savings|https://github.com/yanweiyue/AgentPrune
coordination|2608.16801|multi-agent|Vary team size and shared-file coordination|1902 synthetic coding runs; Claude Sonnet 4.6|About 42% output-token reduction at eight agents on message-heavy tasks|Two task families and one runtime; environment confounds required sealed reruns|replication package claimed; URL not verified'''

def specs():
 rows=[]
 for line in SPEC.splitlines():
  key,ident,category,method,workload,result,limit,code=line.split('|')
  url='https://aclanthology.org/'+ident[4:]+'/' if ident.startswith('acl:') else 'https://arxiv.org/abs/'+ident
  rows.append(dict(key=key,identifier=ident,category=category,url=url,method=method,models_datasets_baselines=workload,reported_improvement=result,limitations=limit,code=code))
 return rows

def build():
 rows=specs()
 if Path('data/routing-annotations.json').exists(): rows+=json.loads(Path('data/routing-annotations.json').read_text())
 for r in rows:
  path=Path('data/raw')/(r['key']+'.html');m=Meta()
  if path.exists():m.feed(path.read_text())
  data=m.meta
  r.update(title=data.get('citation_title',[r.get('title','unverified')])[0],authors='; '.join(data.get('citation_author',[])) or r.get('authors','unverified'),publication_date=data.get('citation_date',data.get('citation_publication_date',['2025' if r['key']=='agserve' else 'unverified']))[0],doi=data.get('citation_doi',['not reported'])[0],status=r.get('status','preprint; later venue not verified'),source_type='primary research',verification='primary page metadata + abstract; selected full-text checks',access_date='2026-09-06',input_tokens='not reported',output_tokens='not reported',cached_tokens='not reported',monetary_cost='not reported',latency='not reported',energy_compute='not reported',quality_metric='task accuracy unless stated otherwise',complexity='high' if r['category'] in ['inference','distillation','tokenization'] else 'medium',interpretation='Mechanism category and deployment caveat are reviewer interpretation; improvement is source report.')
  if r['identifier'].startswith('acl:'):r['status']='peer-reviewed; '+('Findings ACL 2024' if r['key']=='llmlingua2' else 'EMNLP 2023')
  if r['key']=='meancache':r['status']='IPDPS 2025; arXiv v4'
  if r['key']=='onlinecache':r['status']='accepted INFOCOM 2026 per arXiv; v3'
  if r['category'] in ['context','retrieval','agent context','tokenization']:r['input_tokens']=r['reported_improvement']
  if r['category'] in ['output','reasoning','multi-agent']:r['output_tokens']=r['reported_improvement']
  if r['category'] in ['inference','scheduling','KV cache']:r['latency']=r['reported_improvement']
  if r['category']=='routing':r['monetary_cost']=r['reported_improvement']
  if r['key']=='agserve':r['doi']='10.52202/085713-0097'
  if r['key']=='speculative':r['status']='ICML 2023';r['doi']='not reported'
  if r['key']=='distillsteps':r['status']='Findings ACL 2023'
  if r['key']=='tokens2words':r['status']='ICLR 2025 per primary record'
  if r['key']=='pagedattention':r['status']='SOSP 2023'
  statuses={'frugalgpt':'TMLR 2024','routellm':'ICLR 2025','unified':'ICML 2025','mixllm':'NAACL 2025','moa':'ICLR 2025','preble':'ICLR 2025','recomp':'ICLR 2024'}
  if r['key'] in statuses:r['status']=statuses[r['key']]
 Path('data/literature.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
 with open('data/literature.csv','w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 bib=[]
 for r in rows:
  author=r['authors'].replace('; ',' and ')
  year=re.search(r'(19|20)\d{2}',r['publication_date']);year=year.group() if year else ('20'+r['identifier'][:2] if not r['identifier'].startswith('acl:') else r['identifier'][4:8])
  fields={'title':r['title'],'author':author,'year':year,'url':r['url'],'note':r['status']+'; accessed 2026-09-06'}
  if re.match(r'^\d{4}\.\d{4,5}$',r['identifier']):fields.update(eprint=r['identifier'],archivePrefix='arXiv')
  if r['doi']!='not reported':fields['doi']=r['doi']
  bib.append('@misc{'+r['key']+',\n'+',\n'.join('  '+k+' = {'+v.replace('&',r'\&')+'}' for k,v in fields.items())+'\n}')
 Path('references.bib').write_text('\n\n'.join(bib)+'\n')
 print(len(rows),'works; unverified titles:',[r['key'] for r in rows if r['title']=='unverified'])
if __name__=='__main__':build()
