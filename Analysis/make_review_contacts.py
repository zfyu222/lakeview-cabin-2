import json,sys
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];p=ROOT/'ImageText/work';q=Path(sys.argv[1]);m=json.loads((p/'manifest.json').read_text('utf8'));names={x['image_id']:x['sources'][0]['path'] for x in m['images']};jobs=json.loads((q/'package.json').read_text('utf8'))['jobs'];exc=json.loads((ROOT/'ImageText/scope_exclusions.json').read_text('utf8'));jobs=[x for x in jobs if x['image_id'] not in exc]
print('\n'.join(f"{x['id']}: {names[x['image_id']]}" for x in jobs))
for n in range(0,len(jobs),20):
 im=Image.new('RGB',(1560,1650),'#eeeeee');d=ImageDraw.Draw(im)
 for j,x in enumerate(jobs[n:n+20]):
  a=Image.open(p/x['evidence_view']).convert('RGB');a.thumbnail((380,300),Image.Resampling.NEAREST);left=(j%4)*390;top=(j//4)*330;im.paste(a,(left,top+25));d.text((left+4,top+4),'ID '+x['id']+' '+names[x['image_id']][:38],fill='black')
 im.save(q/f'compact-{n//20+1}.png')
print('sheets',(len(jobs)+19)//20)
