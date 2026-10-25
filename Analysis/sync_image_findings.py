"""Expose only saved, validated local findings to the ongoing conversation review."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT.parents[1]/'Tools/image_text'))
from core import read_json,write_json,canonical,digest
import tiered
W=ROOT/'ImageText/work';out,m,s,p=tiered.load_plan(W);findings={};errors=[]
for i,ids in enumerate(p['qwen_batches'],1):
 folder=W/'tiered/qwen'/str(i);path=folder/'vision_findings.json'
 if path.exists():
  f=read_json(path);assert f['scan_hash']==digest(canonical(read_json(folder/'scan.json')))
  for row in f['records']:
   assert row['image_id'] in ids;findings[row['image_id']]=row
 report=folder/'local_vlm/report.json'
 if report.exists():
  r=read_json(report);q=read_json(folder/'queue/jobs.json');jobs={x['id']:x for x in q['jobs']}
  for e in r.get('failures',[]):
   image=jobs[e['id']]['image_id'];errors.append(dict(image_id=image,error=e['error']))
   if image not in findings:findings[image]=dict(image_id=image,presence='uncertain',reason='TOOL_ERROR: model output rejected; explicit visual adjudication required: '+e['error'],proposals=[],semantic_model_result=False)
write_json(W/'tiered/findings.json',dict(plan_hash=p['plan_hash'],images=findings,partial=True));print('Validated saved findings exposed',len(findings));print(tiered.package(W,100))
