"""Read public research sources with system curl; persist metadata and HTTP outcomes."""
import concurrent.futures, hashlib, json, subprocess
from pathlib import Path
URLS={
 'llmlingua':'https://aclanthology.org/2023.emnlp-main.825/',
 'llmlingua2':'https://aclanthology.org/2024.findings-acl.57/',
 'recomp':'https://arxiv.org/abs/2310.04408',
 'lostmiddle':'https://arxiv.org/abs/2307.03172',
 'meancache':'https://arxiv.org/abs/2403.02694',
 'lacache':'https://arxiv.org/abs/2608.01718',
 'onlinecache':'https://arxiv.org/abs/2508.07675',
 'acon':'https://arxiv.org/abs/2510.00615',
 'paritok':'https://arxiv.org/abs/2608.24188',
 'cacheblend':'https://arxiv.org/abs/2405.16444',
 'vcache':'https://openreview.net/forum?id=zF0A0xw3HZ',
 'freshcache':'https://arxiv.org/abs/2607.04281',
 'openai-pricing':'https://developers.openai.com/api/docs/pricing',
 'openai-caching':'https://developers.openai.com/api/docs/guides/prompt-caching',
 'claude-pricing':'https://platform.claude.com/docs/en/about-claude/pricing',
 'gemini-pricing':'https://ai.google.dev/gemini-api/docs/pricing',
 'pypdf-meta':'https://pypi.org/pypi/pypdf/6.0.0/json',
 'crossref-exact':'https://api.crossref.org/works/10.18653/v1/2024.findings-acl.57'
}
def fetch(item):
 key,url=item; path=Path('data/raw')/(key+'.html' if not ('meta' in key or 'crossref' in key) else key+'.json')
 r=subprocess.run(['/usr/bin/curl','-fLsS','--max-time','35','-w','%{http_code}',url,'-o',str(path)],capture_output=True,text=True)
 return {'key':key,'url':url,'http_status':r.stdout,'exit_code':r.returncode,'error':r.stderr.strip(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None}
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex: rows=list(ex.map(fetch,URLS.items()))
 Path('results/source-fetch.json').write_text(json.dumps(rows,indent=2)); print(json.dumps(rows,indent=2))
