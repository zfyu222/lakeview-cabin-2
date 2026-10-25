"""Project-only local Qwen driver: retain invalid replies as tool errors and route them to visual adjudication."""
import sys,time,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT.parents[1]/'Tools/image_text'))
import local_vlm,tiered
from core import read_json,write_json,digest,canonical
failures_all=[]
def resilient(out,endpoint,**kwargs):
 out=Path(out);client=local_vlm.Client(endpoint,local_vlm.MODEL);queue=read_json(out/'queue/jobs.json');started=time.perf_counter();calls=cached=0;failures=[];attempts=[]
 try:
  for i,job in enumerate(queue['jobs'],1):
   image=local_vlm.image_bytes(out/job['crop']);key=digest(canonical(dict(identity=client.identity,image=digest(image),prompt=local_vlm.PROMPT,schema=local_vlm.SCHEMA,options=client.options)));cache=out/'local_vlm/cache'/f'{key}.json';archive=None
   # This exact job already produced a complete invalid model response. Do not repeat it.
   known=next((x for x in old_failures if x['image_id']==job['image_id']),None)
   if known:
    failures.append(known);failures_all.append(known);continue
   try:
    if cache.exists():envelope=read_json(cache);cached+=1
    else:
     archive=out/'local_vlm/raw'/f'{key}-{time.time_ns()}.json';calls+=1
     content,raw,result=client.request(image,archive);gpu=client.gpu_status()
     envelope=dict(content=content,identity=client.identity,gpu=gpu,raw_reply=str(archive.relative_to(out)),usage={k:result.get(k) for k in ('prompt_eval_count','eval_count','total_duration','load_duration','prompt_eval_duration','eval_duration')})
    reply=dict(queue_hash=queue['queue_hash'],records=[dict(envelope['content'],id=job['id'])]);path=out/'local_vlm/resilient_replies'/f'{key}.json';write_json(path,reply);local_vlm.import_findings(out,path);write_json(cache,envelope)
   except Exception as ex:
    item=dict(image_id=job['image_id'],batch=str(out),id=job['id'],error=str(ex),raw_reply=str(archive) if archive else None);failures.append(item);failures_all.append(item)
   finally:
    if archive and archive.exists():
     raw=read_json(archive);attempts.append(dict(image_id=job['image_id'],raw_reply=str(archive),usage={k:raw.get(k) for k in ('prompt_eval_count','eval_count','total_duration')}))
   if i%20==0:print(f'Qwen batch {out.name}: {i}/{len(queue["jobs"])} cached={cached} failures={len(failures)}',flush=True)
  report=dict(requested=len(queue['jobs']),requests=calls,cached=cached,failures=failures,attempts=attempts,elapsed_seconds=time.perf_counter()-started,paid_api_requests=0)
  write_json(out/'local_vlm/resilient_reports'/f'{time.time_ns()}.json',report);return report
 finally:
  client.unload();client.http.close()
W=ROOT/'ImageText/work';old_failures=[]
for reportfile in (W/'tiered/qwen').glob('*/local_vlm/report.json'):
 r=read_json(reportfile);q=read_json(reportfile.parents[1]/'queue/jobs.json');jobs={x['id']:x for x in q['jobs']}
 for f in r.get('failures',[]):
  job=jobs[f['id']];raw=next((a['raw_reply'] for a in r.get('request_usage',[]) if a['id']==f['id']),None)
  old_failures.append(dict(image_id=job['image_id'],batch=str(reportfile.parents[1]),id=f['id'],error=f['error'],raw_reply=str(reportfile.parents[1]/raw) if raw else None))
local_vlm.run=resilient
result=tiered.qwen_batches(W)
# These entries explicitly represent routing errors, never a model's semantic judgment.
findings=read_json(W/'tiered/findings.json')
for f in failures_all:
 findings['images'][f['image_id']]=dict(image_id=f['image_id'],presence='uncertain',reason='TOOL_ERROR: local model output rejected; direct conversation-agent visual review required. '+f['error'],proposals=[],tool_error=f,semantic_model_result=False)
write_json(W/'tiered/findings.json',findings);write_json(W/'tiered/qwen_failures.json',failures_all)
print(json.dumps(dict(result=result['invocation'],tool_errors=len(failures_all),agent=tiered.package(W)),ensure_ascii=False))
