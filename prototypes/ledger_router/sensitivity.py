"""Quality threshold and verifier-cost sensitivity; no paid calls."""
import copy,json
from pathlib import Path
from core import Router,calibrate
from benchmark import make_workload,summarize
HERE=Path(__file__).resolve().parent
cfg=json.loads((HERE/'config.json').read_text());train,test=make_workload(cfg['seed']);cal=calibrate(train);out=[]
for target in [.95,.99,.999]:
 for fee in [0,.000015,.001]:
  c=copy.deepcopy(cfg);c.update(quality_target=target,verifier_usd=fee)
  for scenario in ['stationary','cold','wording_drift']:
   router=Router(c,cal,'full');records=[router.run(q) for q in test if q['scenario']==scenario]
   out.append({'quality_target':target,'verifier_usd':fee,'scenario':scenario,**summarize(records)})
(HERE/'results/sensitivity.json').write_text(json.dumps(out,indent=2))
# Calibration is offline local computation here. This counterfactual ledger prices the
# 600 small-model calibration responses with the illustrative cache behavior.
r=Router(cfg,cal,'cheap');calrows=[r.run(q) for q in train]
(HERE/'results/calibration-cost.json').write_text(json.dumps({'actual_api_spend_usd':0,'label':'counterfactual calibration-response serving cost; labels local, no teacher expense','calibration_examples':len(train),'simulated_serving':summarize(calrows)},indent=2))
print(len(out),'sensitivity settings evaluated')
