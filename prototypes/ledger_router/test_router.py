import json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from core import Router,calibrate,signature,wilson_lower
from benchmark import make_workload
from shared.accounting import Usage,Rates,PrefixCache,openai_usage,anthropic_usage,gemini_usage
class Tests(unittest.TestCase):
 def setUp(self):
  self.cfg=json.loads((Path(__file__).parent/'config.json').read_text());self.train,self.test=make_workload();self.cal=calibrate(self.train)
 def test_quality_lower_bound(self):
  self.assertLess(wilson_lower(3,3),.95);self.assertGreater(wilson_lower(400,400),.95)
 def test_cost_partition(self):
  self.assertAlmostEqual(Rates(2,8,.2,2.5).cost(Usage(100,20,40,10,5)),(50*2+20*8+40*.2+10*2.5)/1e6)
  with self.assertRaises(ValueError):Usage(10,1,7,4)
  with self.assertRaises(ValueError):Usage(10,1,0,0,2)
 def test_provider_normalization(self):
  self.assertEqual(anthropic_usage({'input_tokens':10,'output_tokens':5,'cache_read_input_tokens':20}).input_tokens,30)
  self.assertEqual(gemini_usage({'promptTokenCount':10,'candidatesTokenCount':5,'thoughtsTokenCount':7}).output_tokens,12)
  self.assertEqual(openai_usage({'input_tokens':10,'output_tokens':12,'output_tokens_details':{'reasoning_tokens':7}}).output_tokens,12)
 def test_tenant_version_negation_isolation(self):
  q=self.test[0]
  for field,value in [('tenant','different'),('version',999),('blocked',not q['blocked'])]:self.assertNotEqual(signature(q),signature({**q,field:value}))
 def test_expiry_and_model_isolation(self):
  c=PrefixCache(4,2,10);c.put(('A','m1'),[1,2,3,4,5],0)
  self.assertEqual(c.peek(('A','m1'),[1,2,3,4,9],1),4)
  self.assertEqual(c.peek(('A','m2'),[1,2,3,4,5],1),0)
  self.assertEqual(c.peek(('A','m1'),[1,2,3,4,5],10),0)
 def test_fallback_charged(self):
  r=Router(self.cfg,self.cal,'cascade').run(self.test[0]);self.assertTrue(r['fallback']);self.assertEqual(len(r['calls']),2)
  self.assertGreater(r['cost_usd'],sum(c['cost_usd'] for c in r['calls']))
 def test_safe_quality_and_unsafe_failure(self):
  subset=[q for q in self.test if q['scenario']=='tenant_version_attack']
  good=Router(self.cfg,self.cal,'full');bad=Router(self.cfg,self.cal,'unsafe_cache')
  self.assertGreaterEqual(sum(good.run(q)['correct'] for q in subset)/len(subset),.95)
  self.assertTrue(any(not bad.run(q)['correct'] for q in subset))
 def test_scenario_names_do_not_affect_routing(self):
  q=self.test[0];a=Router(self.cfg,self.cal,'cheap').run(q);b=Router(self.cfg,self.cal,'cheap').run({**q,'scenario':'arbitrary'})
  self.assertEqual(a['calls'],b['calls'])
 def test_fully_cold_has_no_prefix_reads(self):
  r=Router(self.cfg,self.cal,'full')
  self.assertEqual(sum(c['cached_tokens'] for q in self.test if q['scenario']=='cold' for c in r.run(q)['calls']),0)
 def test_rejection_rate_not_accuracy(self):
  rows=[{**self.test[0],'amount':900,'blocked':True} for _ in range(600)]
  cal=calibrate(rows);self.assertEqual(cal['exception']['point'],1);self.assertEqual(cal['exception']['reject_rate'],1)
 def test_silent_verifier_failure(self):
  from core import model_answer,verify,gold
  q={**self.test[0],'amount':419,'blocked':False,'wording':'normal'}
  a=model_answer('small',q);self.assertTrue(verify(q,a));self.assertNotEqual(a,gold(q))
 def test_billed_retry(self):
  r=Router(self.cfg,self.cal,'strong').run({**self.test[0],'transient':True})
  self.assertEqual(len(r['calls']),2);self.assertTrue(r['calls'][0]['error']);self.assertGreater(r['calls'][0]['cost_usd'],0)
 def test_nonfinite_rejected(self):
  for v in [float('nan'),float('inf')]:
   with self.assertRaises(ValueError):Rates(v,1,1,1)
   with self.assertRaises(ValueError):Rates(1,1,1,1).cost(Usage(1),tool_usd=v)
 def test_wording_identity(self):
  q=self.test[0];self.assertNotEqual(signature(q),signature({**q,'wording':'shifted'}))
if __name__=='__main__':unittest.main()
