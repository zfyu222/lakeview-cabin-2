from pathlib import Path
import UnityPy,json
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'Game/Lakeview Cabin 2_Data';hashes=json.loads((ROOT/'Analysis/source_hashes.json').read_text('utf8'));env=UnityPy.load(*[str(D/f) for f in hashes]);out=[]
for o in env.objects:
 if o.type.name!='Sprite':continue
 t=o.read_typetree();rd=t['m_RD'];ref=rd['texture'];sf=o.assets_file
 file=Path(sf.name).name if ref['m_FileID']==0 else Path(sf.externals[ref['m_FileID']-1].path).name
 out.append(dict(file=Path(sf.name).name,path_id=o.path_id,name=t['m_Name'],texture_file=file,texture_id=ref['m_PathID'],rect=t['m_Rect'],pivot=t['m_Pivot'],texture_rect=rd['textureRect'],settings=rd['settingsRaw']))
(ROOT/'Analysis/sprite_slices.json').write_text(json.dumps(out),encoding='utf8');print(len(out),'sprite slices')
