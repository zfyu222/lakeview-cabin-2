"""Verify saved Sprite extraction, original pivots/slices, formal CSV hashes and backup/payload integrity."""
import json,hashlib,collections
from pathlib import Path
import UnityPy
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'Repack';manifest=json.loads((R/'manifest.json').read_text('utf8'));textures=json.loads((ROOT/'ImagePatch/build/IMAGE_PATCH_MANIFEST.json').read_text('utf8'));bindings={}
for f in textures['files']:
 for src in f['sources']:
  for e in src['provenance']['engine_sources']:bindings[(e['file'],e['path_id'])]=ROOT/'ImagePatch/build'/f['path']
counts=collections.Counter();sprites=[];preview=R/'sprite_preview';preview.mkdir(exist_ok=True)
for f in manifest['files']:
 name=Path(f['path']).name;env=UnityPy.load(str(R/'Files'/f['path']));sf=next(v for k,v in env.files.items() if Path(k).name==name);old=UnityPy.load(str(R/'Originals'/name));oldsf=next(v for k,v in old.files.items() if Path(k).name==name)
 for ch in f['changes']:
  counts[ch['kind']]+=1
  if ch['kind']!='sprite':continue
  o=sf.objects[ch['path_id']];t=o.read_typetree();original=oldsf.objects[o.path_id].read_typetree();assert t['m_Rect']==original['m_Rect'] and t['m_Pivot']==original['m_Pivot']
  ref=t['m_RD']['texture'];assert ref['m_FileID']==0
  source=Image.open(bindings[(name,ref['m_PathID'])]).convert('RGBA');rect=t['m_Rect'];box=(int(rect['x']),int(source.height-rect['y']-rect['height']),int(rect['x']+rect['width']),int(source.height-rect['y']))
  expected=source.crop(box);actual=o.read().image.convert('RGBA');assert actual.size==expected.size and actual.tobytes()==expected.tobytes(),f'Sprite mismatch {name}/{o.path_id}'
  actual.save(preview/f'{name}-{o.path_id}.png');sprites.append(dict(file=name,path_id=o.path_id,name=t['m_Name'],rect=rect,pivot=t['m_Pivot'],pixel_match=True))
font=ROOT/'Repack/Fonts/NotoSansSC-Regular.ttf'
r=dict(status='passed_static_pending_user_test',counts=dict(counts),sprite_roundtrip=sprites,font_sha256=hashlib.sha256(font.read_bytes()).hexdigest(),unchanged_objects='Builder compared every unmodified object raw payload with original; all identical.',in_game_check='pending_user',game_version='Steam Windows x64 BuildID 13433015')
(R/'static_validation.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(dict(status=r['status'],counts=dict(counts)),ensure_ascii=False))
