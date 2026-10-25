"""Install/restore the exact verified payload, with hash checks and backups."""
from pathlib import Path
import json,hashlib,shutil,argparse
ROOT=Path(__file__).resolve().parents[1];GAME=(ROOT/'Game').resolve();R=ROOT/'Repack'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('action',choices=['install','restore']);a=p.parse_args()
m=json.loads((R/'manifest.json').read_text('utf8'))
# Validate the complete operation before writing any game file.
for f in m['files']:
 target=GAME/f['path'];assert target.resolve().is_relative_to(GAME)
 original=R/'Originals'/Path(f['path']).name;payload=R/'Files'/f['path']
 assert sha(original)==f['original_sha256'];assert sha(payload)==f['patched_sha256']
 assert sha(target) in (f['original_sha256'],f['patched_sha256']),f'Unexpected game version: {target}'
for f in m['files']:
 target=GAME/f['path'];source=R/'Originals'/Path(f['path']).name if a.action=='restore' else R/'Files'/f['path']
 shutil.copy2(source,target);expected=f['original_sha256'] if a.action=='restore' else f['patched_sha256'];assert sha(target)==expected
print(json.dumps({'action':a.action,'files':len(m['files']),'status':'verified','game_root':str(GAME)},ensure_ascii=False))
