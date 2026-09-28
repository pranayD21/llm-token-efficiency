"""Optional online check. A browser challenge is not classified as verified content."""
import concurrent.futures,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
urls={r['url'] for r in json.loads((ROOT/'data/literature.json').read_text())}
for p in (ROOT/'docs').glob('*.md'):
 urls.update(re.findall(r'\]\((https?://[^)]+)\)',p.read_text()))
def check(url):
 r=subprocess.run(['/usr/bin/curl','-LsS','--max-time','20','-w','\n%{http_code}',url.split('#')[0]],capture_output=True,text=True,errors="replace")
 body,_,status=r.stdout.rpartition('\n');blocked='Verifying your browser' in body or '<title>Just a moment' in body
 return {'url':url,'status':status,'transport_exit':r.returncode,'content_blocked':blocked,'verified_access':r.returncode==0 and status=='200' and not blocked}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:out=list(ex.map(check,sorted(urls)))
(ROOT/'results/link-checks.json').write_text(json.dumps(out,indent=2));print(json.dumps({'checked':len(out),'accessible':sum(x['verified_access'] for x in out),'exceptions':[x for x in out if not x['verified_access']]},indent=2))
