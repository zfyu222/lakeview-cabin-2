"""Build reversible Unity asset replacements from formally validated translations."""
from pathlib import Path
import json,csv,hashlib,collections,sys,struct,copy
import UnityPy
from PIL import Image
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator
from UnityPy.helpers import TypeTreeHelper as H
from UnityPy.enums import TextureFormat
from fontTools.ttLib import TTFont
ROOT=Path(__file__).resolve().parents[1];DATA=(ROOT/'Game/Lakeview Cabin 2_Data').resolve()
OUT=ROOT/'Repack/Files/Lakeview Cabin 2_Data';BACK=ROOT/'Repack/Originals'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text('utf-8-sig'))
def csvs(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return [r[0] for r in csv.reader(f)]
def validated(source,translated,report):
 r=load(report);a=csvs(source);b=csvs(translated)
 assert r['status']=='passed' and r['semantic_review']=='full'
 assert r['source_sha256']==sha(source) and r['translation_sha256']==sha(translated)
 assert r['records']==len(a)==len(b)
 return dict(zip(a,b))
translations=validated(ROOT/'lakeview-cabin-2_text.csv',ROOT/'lakeview-cabin-2_text_translated.csv',ROOT/'TranslateFiles/reports/final_validation.json')
with TTFont(ROOT/'Repack/Fonts/NotoSansSC-Regular.ttf') as font:
 missing=sorted({c for t in translations.values() for c in t if not c.isspace() and ord(c) not in font.getBestCmap()})
 assert not missing, f'Missing CJK glyphs: {missing}'
mapdata=load(ROOT/'Analysis/source_mapping.json')
image_manifest=load(ROOT/'ImagePatch/build/IMAGE_PATCH_MANIFEST.json')
assert image_manifest['status']=='ready_for_engine_adapter' and image_manifest['mode']=='texture'
validated(ROOT/'lakeview-cabin-2_images_text.csv',ROOT/'lakeview-cabin-2_images_text_translated.csv',ROOT/'TranslateFiles/image-text/TranslateFiles/reports/final_validation.json')
assert image_manifest['translation_sha256']==sha(ROOT/'lakeview-cabin-2_images_text_translated.csv')
byfile=collections.defaultdict(list)
for r in mapdata['occurrences']:byfile[r['file']].append(('text',r))
for f in image_manifest['files']:
 image=ROOT/'ImagePatch/build'/f['path'];assert sha(image)==f['sha256']
 for source in f['sources']:
  for ref in source['provenance']['engine_sources']:byfile[ref['file']].append(('texture',dict(ref,image=str(image))))
# English letters use tight meshes; Chinese strokes require a full-rectangle mesh inside each original sprite slice.
texture_bindings={}
for f in image_manifest['files']:
 for source in f['sources']:
  for ref in source['provenance']['engine_sources']:
   texture_bindings[(ref['file'],ref['path_id'])]=dict(image_id=f['image_id'],width=ref['width'],height=ref['height'])
sprite_env=UnityPy.load(*[str(DATA/f) for f in load(ROOT/'Analysis/source_hashes.json')])
for o in sprite_env.objects:
 if o.type.name!='Sprite':continue
 t=o.read_typetree();rd=t['m_RD'];ref=rd['texture'];sf=o.assets_file
 file=Path(sf.name).name if ref['m_FileID']==0 else Path(sf.externals[ref['m_FileID']-1].path).name
 binding=texture_bindings.get((file,ref['m_PathID']))
 if not binding:continue
 rect=t['m_Rect'];top=binding['height']-rect['y']-rect['height'];left=rect['x'];right=left+rect['width'];bottom=top+rect['height']
 regions=[x['box'] for x in image_manifest['entries'] if x['image_id']==binding['image_id']]
 if not any(min(right,b[2])>max(left,b[0]) and min(bottom,b[3])>max(top,b[1]) for b in regions):continue
 byfile[Path(sf.name).name].append(('sprite',dict(path_id=o.path_id,texture_width=binding['width'],texture_height=binding['height'])))
del sprite_env

# The credits font is a dynamic TrueType font; swap its data while retaining all object IDs.
font_ref=next(x for x in load(ROOT/'Analysis/fonts.json') if x['name']=='PixelOperator')
byfile[font_ref['file']].append(('font',font_ref))
source_hashes=load(ROOT/'Analysis/source_hashes.json');OUT.mkdir(parents=True,exist_ok=True);BACK.mkdir(parents=True,exist_ok=True)
g=TypeTreeGenerator('2019.4.34f1');g.load_local_dll_folder(str(DATA/'Managed'))
n=g.get_nodes_up('UnityEngine.UI.dll','UnityEngine.UI.Text')
H.read_typetree_boost=None
next(c for c in n.m_Children if c.m_Name=='m_Enabled').m_MetaFlag|=16384
report=[]
for filename,changes in sorted(byfile.items()):
 original=DATA/filename
 assert sha(original)==source_hashes[filename],f'Game source changed: {filename}'
 backup=BACK/filename
 if backup.exists():assert sha(backup)==source_hashes[filename]
 else:backup.write_bytes(original.read_bytes())
 e=UnityPy.load(str(original));sf=next(sf for k,sf in e.files.items() if Path(k).name==filename);done=[]
 for kind,r in changes:
  o=sf.objects[r['path_id']]
  if kind=='text':
   t=o.read_typetree(n);assert t[r['field']]==r['text']
   text=t[r['field']]
   for src,dst in translations.items():
    assert text.count(src)==1;text=text.replace(src,dst)
   t[r['field']]=text;o.save_typetree(t,nodes=n)
  elif kind=='font':
   t=o.read_typetree();t['m_FontData']=list((ROOT/'Repack/Fonts/NotoSansSC-Regular.ttf').read_bytes());t['m_FontNames']=['Noto Sans SC'];o.save_typetree(t)
  elif kind=='sprite':
   t=o.read_typetree();rd=t['m_RD'];rect=t['m_Rect'];ppu=t['m_PixelsToUnits'];pivot=t['m_Pivot']
   assert not t.get('m_Bones'), 'Skinned sprite needs a separate adapter'
   assert not rd['settingsRaw']&1 and not t['m_SpriteAtlas']['m_PathID'], 'Packed sprites need a separate adapter'
   rd['textureRect']=copy.deepcopy(rect);rd['textureRectOffset']=dict(x=0.0,y=0.0)
   rd['uvTransform']=dict(x=ppu,y=rect['x']+pivot['x']*rect['width'],z=ppu,w=rect['y']+pivot['y']*rect['height'])
   x0=-pivot['x']*rect['width']/ppu;y0=-pivot['y']*rect['height']/ppu;x1=x0+rect['width']/ppu;y1=y0+rect['height']/ppu
   vertices=[(x0,y0),(x0,y1),(x1,y0),(x1,y1)];uv=rd['uvTransform']
   data=b''.join(struct.pack('<3f',x,y,0) for x,y in vertices)
   data+=b''.join(struct.pack('<2f',(x*uv['x']+uv['y'])/r['texture_width'],(y*uv['z']+uv['w'])/r['texture_height']) for x,y in vertices)
   vd=rd['m_VertexData'];vd['m_VertexCount']=4;vd['m_DataSize']=data
   for ch in vd['m_Channels']:ch.update(stream=0,offset=0,format=0,dimension=0)
   vd['m_Channels'][0].update(stream=0,offset=0,format=0,dimension=3);vd['m_Channels'][4].update(stream=1,offset=0,format=0,dimension=2)
   rd['m_IndexBuffer']=struct.pack('<6H',0,1,2,2,1,3);rd['settingsRaw']&=~64
   sub=copy.deepcopy(rd['m_SubMeshes'][0]);sub.update(firstByte=0,indexCount=6,topology=0,baseVertex=0,firstVertex=0,vertexCount=4);sub['localAABB']={'m_Center':dict(x=(x0+x1)/2,y=(y0+y1)/2,z=0.0),'m_Extent':dict(x=(x1-x0)/2,y=(y1-y0)/2,z=0.0)};rd['m_SubMeshes']=[sub]
   o.save_typetree(t)
  else:
   im=Image.open(r['image']).convert('RGBA');t=o.read();assert (t.m_Width,t.m_Height)==im.size
   t.set_image(im,target_format=TextureFormat.RGBA32,mipmap_count=1);t.save()
  done.append(dict(kind=kind,path_id=r['path_id']))
 target=OUT/filename;target.write_bytes(sf.save())
 # Round-trip verification: every modified resource remains readable and exact.
 e2=UnityPy.load(str(target));sf2=next(sf for k,sf in e2.files.items() if Path(k).name==filename)
 for kind,r in changes:
  o=sf2.objects[r['path_id']]
  if kind=='texture':assert o.read().image.convert('RGBA').tobytes()==Image.open(r['image']).convert('RGBA').tobytes()
  elif kind=='sprite':assert o.read_typetree()['m_RD']['m_VertexData']['m_VertexCount']==4 and len(o.read_typetree()['m_RD']['m_IndexBuffer'])==12
  elif kind=='font':assert bytes(o.read_typetree()['m_FontData'])==(ROOT/'Repack/Fonts/NotoSansSC-Regular.ttf').read_bytes()
  else:
   t=o.read_typetree(n)
   for dst in translations.values():assert dst in t[r['field']]
 changed_ids={r['path_id'] for _,r in changes}
 for pid,obj in sf.objects.items():
  if pid not in changed_ids:assert obj.get_raw_data()==sf2.objects[pid].get_raw_data(),f'Unrelated object changed: {filename}/{pid}'
 report.append(dict(path='Lakeview Cabin 2_Data/'+filename,original_sha256=source_hashes[filename],patched_sha256=sha(target),bytes=target.stat().st_size,changes=done))
 print(filename,'verified',len(done),flush=True)
(ROOT/'Repack/manifest.json').write_text(json.dumps(dict(status='static_verified_pending_user_test',files=report),ensure_ascii=False,indent=2),encoding='utf8')
