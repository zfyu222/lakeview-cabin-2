"""Reproducible read-only Unity text and texture extraction."""
import sys,json,re,hashlib,collections
from pathlib import Path
import UnityPy
from UnityPy.helpers import TypeTreeHelper as H
ROOT=Path(__file__).resolve().parents[1]
s=(ROOT/'extract_fsm.py').read_text('utf-8').split('results = []')[0]
exec(s)
H.read_typetree_boost=None
old_get_nodes=get_nodes
def fixed_nodes(*args):
 n=old_get_nodes(*args)
 if n is None:return n
 def fix(x):
  if x.m_Name=='m_Enabled' and x.m_Level==1:x.m_MetaFlag|=16384
  if x.m_Children and x.m_Children[0].m_Type=='Array' and x.m_Type in H.FUNCTION_READ_MAP and x.m_Children[0].m_Children[1].m_Type!='char':x.m_Type='vector'
  for c in x.m_Children:fix(c)
 fix(n);return n
records=[];values=[];errors=[];textures=[];fonts=[];seen={};counts=collections.Counter()
def walk(v,trail,base):
 if isinstance(v,dict):
  for k,x in v.items():walk(x,trail+[k],base)
 elif isinstance(v,list):
  for i,x in enumerate(v):walk(x,trail+[i],base)
 elif isinstance(v,str) and v.strip():
  if (trail[-1]=='value' and ('fsmStringParams' in trail or 'stringVariables' in trail)) or 'preFillStringList' in trail:
   values.append(dict(base,field=trail,text=v))
for full,sf in list(env.files.items()):
 fn=Path(full).name
 for obj in sf.objects.values():
  kind=obj.type.name;counts[kind]+=1
  base=dict(file=fn,path_id=obj.path_id,type=kind)
  try:
   if kind=='MonoBehaviour':
    sk=script_of(obj)
    if not sk:continue
    if sk[1] not in ('PlayMakerFSM','PlayMakerArrayListProxy','PlayMakerHashTableProxy','UnityEngine.UI.Text','TMPro.TextMeshPro','TMPro.TextMeshProUGUI'):continue
    tree=obj.read_typetree(fixed_nodes(*sk));base['script']=sk[1]
    if sk[1]=='PlayMakerFSM':walk(tree,[],dict(base,fsm=tree.get('fsm',{}).get('name')))
    elif sk[1].startswith('PlayMaker'):walk(tree,[],base)
    else:
     for k in ('m_Text','m_text'):
      if tree.get(k,'').strip():records.append(dict(base,field=k,text=tree[k]))
   elif kind in ('TextMesh','GUIText'):
    t=obj.read_typetree()
    if t.get('m_Text','').strip():records.append(dict(base,field='m_Text',text=t['m_Text'],font=t.get('m_Font')))
   elif kind=='Font':
    t=obj.read_typetree();fonts.append(dict(base,name=t.get('m_Name'),font_names=t.get('m_FontNames'),data_size=len(t.get('m_FontData',[]))))
   elif kind=='Texture2D':
    t=obj.read();img=t.image
    if img is None:continue
    digest=hashlib.sha256(img.convert('RGBA').tobytes()+str(img.size).encode()).hexdigest()
    name=seen.get(digest)
    if not name:
     name=f'{len(seen):05d}_{re.sub("[^A-Za-z0-9_-]","_",t.m_Name)[:90]}.png';seen[digest]=name
     img.save(ROOT/'ImageText/exported'/name)
    textures.append(dict(base,name=t.m_Name,path=name,width=img.width,height=img.height))
  except Exception as e:errors.append(dict(base,error=str(e)))
 print(fn,'display',len(records),'fsm',len(values),'textures',len(seen),'errors',len(errors),flush=True)
for name,data in [('display_text',records),('playmaker_values',values),('textures',textures),('fonts',fonts),('errors',errors),('inventory',dict(counts))]:
 (ROOT/'Analysis'/f'{name}.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
print('DONE',len(records),len(values),len(seen),len(errors))

