"""Extract only text-assignment actions, not internal FSM identifiers."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
s=(ROOT/'Analysis/extract_assets.py').read_text('utf8').split('records=[]')[0]
exec(s)
results=[]
for full,sf in list(env.files.items()):
 for o in sf.objects.values():
  if o.type.name!='MonoBehaviour':continue
  raw=o.get_raw_data()
  if not any(x in raw for x in (b'UiTextSetText',b'SetTextMeshText',b'SetGUIText',b'DOTweenTextText')):continue
  sk=script_of(o)
  if not sk or sk[1]!='PlayMakerFSM':continue
  t=o.read_typetree(fixed_nodes(*sk))
  for i,st in enumerate(t['fsm']['states']):
   ad=st['actionData']
   if not any(x.endswith(('.UiTextSetText','.SetTextMeshText','.SetGUIText','.DOTweenTextText')) for x in ad['actionNames']):continue
   results.append(dict(file=Path(full).name,path_id=o.path_id,fsm=t['fsm']['name'],state_index=i,state=st['name'],actionData=ad,variables=t['fsm']['variables']['stringVariables']))
(ROOT/'Analysis/text_action_context.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8')
print('text states',len(results))
