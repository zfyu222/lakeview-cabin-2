"""Game-specific adapter for confirmed image overlays; preserves alpha and mirrored credits."""
from pathlib import Path
import json,math,hashlib,collections,csv
from PIL import Image,ImageDraw,ImageFont,ImageOps
ROOT=Path(__file__).resolve().parents[1];W=ROOT/'ImageText/work';SRC=ROOT/'ImagePatch/overlay';OUT=ROOT/'ImagePatch/build'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text('utf-8-sig'))
def rows(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return [r[0] for r in csv.reader(f)]
m=load(SRC/'IMAGE_PATCH_MANIFEST.json');assert m['status']=='ready_for_engine_adapter' and m['mode']=='overlay'
assert m['source_sha256']==sha(ROOT/'lakeview-cabin-2_images_text.csv') and m['translation_sha256']==sha(ROOT/'lakeview-cabin-2_images_text_translated.csv')
a=rows(ROOT/'lakeview-cabin-2_images_text.csv');groups=collections.defaultdict(list)
for e in m['entries']:
 if a[e['csv_row']-1]!=e['text']:groups[e['image_id']].append(e)
OUT.mkdir(parents=True,exist_ok=False);(OUT/'images').mkdir()
fontpath=ROOT/'Repack/Fonts/NotoSansSC-Regular.ttf';files=[];entries=[];layout=[]
slices=load(ROOT/'Analysis/sprite_slices.json')
for key,items in groups.items():
 im=Image.open(W/'images'/f'{key}.png').convert('RGBA')
 for e in items:
  l,t,r,b=[int(round(v)) for v in e['box']]
  # Fit replacement ink within the actual Unity sprite slice; source confirmation boxes remain immutable.
  refs={(ref['file'],ref['path_id']) for source in e['sources'] for ref in source['provenance']['engine_sources']}
  candidates=[]
  for sp in slices:
   if (sp['texture_file'],sp['texture_id']) not in refs:continue
   sr=sp['rect'];sl=sr['x'];st=im.height-sr['y']-sr['height'];rr=sl+sr['width'];bb=st+sr['height'];area=max(0,min(r,rr)-max(l,sl))*max(0,min(b,bb)-max(t,st))
   if area:candidates.append((area,sl,st,rr,bb))
  if candidates:
   _,sl,st,rr,bb=max(candidates);l=max(l,int(sl));t=max(t,int(st));r=min(r,int(rr));b=min(b,int(bb))
  w,h=r-l,b-t
  assert w>0 and h>0
  name=e['sources'][0]['path'];text=e['text']
  # All transparent title/menu sheets can be cleanly replaced inside their confirmed regions.
  region=im.crop((l,t,r,b));alpha=region.getchannel('A');transparent=alpha.getextrema()[0]==0 and sum(alpha.getdata())/(255*w*h)<.65
  if transparent:base=Image.new('RGBA',(w,h),(0,0,0,0))
  else:
   background=collections.Counter(region.getdata()).most_common(1)[0][0];base=Image.new('RGBA',(w,h),background)
  outline='00165_' in name and l>=512
  mirrored='FauxCredits2' in name
  gold=('LakeviewCabin1TitleCard' in name and 'Lakeview' in a[e['csv_row']-1]) or 'LakeviewCabin1GameOver' in name
  ink_color=(255,215,0,255) if gold else (255,255,255,255)
  fit=None
  for size in range(min(120,h*2),5,-1):
   font=ImageFont.truetype(str(fontpath),size);lines=text.split('\n');boxes=[font.getbbox(line) for line in lines]
   heights=[max(1,z[3]-z[1]) for z in boxes];widths=[font.getlength(line) for line in lines];gap=max(1,size//8)
   if max(widths,default=0)<=w-2 and sum(heights)+gap*(len(lines)-1)<=h-1:fit=(font,lines,heights,gap,size);break
  if fit is None:raise ValueError(f'Cannot fit {name}: {text!r} in {w}x{h}')
  font,lines,heights,gap,size=fit;ink=Image.new('RGBA',(w,h),(0,0,0,0));draw=ImageDraw.Draw(ink);y=(h-sum(heights)-gap*(len(lines)-1))//2
  for line,height in zip(lines,heights):
   x=(w-font.getlength(line))/2
   draw.text((x,y),line,font=font,fill=(255,255,255,0) if outline else ink_color,stroke_width=1 if outline or gold else 0,stroke_fill='white' if outline else 'black',anchor='lt');y+=height+gap
  if mirrored:ink=ImageOps.mirror(ink)
  base.alpha_composite(ink);im.paste(base,(l,t));entries.append(e);layout.append(dict(image_id=key,source=name,box=[l,t,r,b],text=text,font_size=size,transparent=transparent,outline=outline,mirrored=mirrored))
 path=OUT/'images'/f'{key}.png';im.save(path);files.append(dict(path=path.relative_to(OUT).as_posix(),sha256=sha(path),image_id=key,sources=items[0]['sources']))
m.update(mode='texture',files=files,entries=entries,adapter='lakeview_alpha_and_mirrored_credits_v1',overlay_manifest_sha256=sha(SRC/'IMAGE_PATCH_MANIFEST.json'),layout=layout)
(OUT/'IMAGE_PATCH_MANIFEST.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8')
print('Rendered',len(files),'textures,',len(entries),'changed text regions; unchanged keys, numbers, names preserved.')
