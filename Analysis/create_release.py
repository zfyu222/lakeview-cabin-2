"""Package exactly the user-tested files with the shared release skill, then verify ZIP layout and sparse clean-copy installation."""
from pathlib import Path
import json,subprocess,sys,zipfile,hashlib,shutil,tempfile
P=Path(__file__).resolve().parents[1];D=P/'Dispatch';m=json.loads((D/'release_metadata.json').read_text('utf8'));payload=json.loads((P/'Repack/manifest.json').read_text('utf8'))['files']
args=[str(P.parents[1]/'Tools/AINiee/venv/Scripts/python.exe'),str(P.parents[1]/'.agents/skills/game-release-patch/scripts/create_release_patch.py'),'--project',str(P)]
args.extend(['--version','1.0'])
for key in ('game_name','introduction','coverage','game_version','platform','release_date','install','uninstall','verification','known_issues'):args.extend(['--'+key.replace('_','-'),m[key]])
for f in payload:args.extend(['--include',str(P/'Repack/Files'/f['path'])+'='+f['path']])
subprocess.run(args+['--dry-run'],check=True);subprocess.run(args,check=True)
archive=D/'湖景小屋2_子非鱼汉化1.0.zip';stage=D/'Files';reserved={'补丁说明.txt','PATCH_MANIFEST.json','SHA256SUMS.txt'}
with zipfile.ZipFile(archive) as z:
 for n in reserved:(stage/n).write_bytes(z.read(n))
guide=(stage/'补丁说明.txt').read_text('utf-8-sig')
guide=guide.replace('补丁后续可能会更新，建议关注或订阅本项目的 GitHub 仓库 / Releases，及时获取新版补丁。','补丁后续可能会更新，建议关注或订阅本项目的 GitHub 仓库 / Releases，及时获取新版补丁。\n项目：https://github.com/zfyu222/lakeview-cabin-2\n下载：https://github.com/zfyu222/lakeview-cabin-2/releases')
guide=guide.replace('如遇问题，请附上游戏版本、平台、安装步骤、报错截图和日志。请勿在补丁中传播游戏本体或其他受版权保护的原始资源。','反馈地址：https://github.com/zfyu222/lakeview-cabin-2/issues\n如遇问题，请附上游戏版本、平台、问题场景和截图。请勿传播游戏本体或原始游戏资源。')
(stage/'补丁说明.txt').write_text(guide,encoding='utf-8-sig')

# The final ZIP is generated solely from Dispatch/Files.
temp=archive.with_suffix('.tmp.zip')
with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for f in sorted(stage.rglob('*')):
  if f.is_file():z.write(f,f.relative_to(stage).as_posix())
temp.replace(archive)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected={f['path'] for f in payload}|reserved
with zipfile.ZipFile(archive) as z:
 assert set(z.namelist())==expected;assert z.testzip() is None
 guide=z.read('补丁说明.txt');assert guide.startswith(b'\xef\xbb\xbf');assert guide.decode('utf-8-sig').startswith('《湖景小屋2》子非鱼AI汉化补丁 v1.0')
 for name in z.namelist():assert not Path(name).is_absolute() and '..' not in Path(name).parts
 with tempfile.TemporaryDirectory(prefix='lakeview-release-check-') as td:
  root=Path(td)
  for f in payload:
   dest=root/f['path'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(P/'Repack/Originals'/Path(f['path']).name,dest);assert sha(dest)==f['original_sha256']
  z.extractall(root)
  checks=json.loads((root/'PATCH_MANIFEST.json').read_text('utf8'))
  for f in checks['files']:assert sha(root/f['path'])==f['sha256']
  for line in (root/'SHA256SUMS.txt').read_text('utf8').splitlines():h,n=line.split('  ',1);assert sha(root/n)==h
  for f in payload:assert sha(root/f['path'])==f['patched_sha256']
report=dict(status='passed',archive=archive.name,sha256=sha(archive),size=archive.stat().st_size,files=len(expected),payload_files=len(payload),checks=['shared release-check passed','ZIP exact file allowlist','UTF-8 BOM Chinese guide','ZIP integrity','sparse clean-copy installation over all seven original files','all installed payload and checksum hashes match user-tested payload'],note='Archive install simulation is static; user in-game verification is recorded separately. No game launch by agent.')
(D/'release_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');(D/'SHA256SUMS.txt').write_text(report['sha256']+'  '+archive.name+'\n',encoding='utf8');(D/'补丁说明.txt').write_bytes((stage/'补丁说明.txt').read_bytes());(D/'PATCH_MANIFEST.json').write_bytes((stage/'PATCH_MANIFEST.json').read_bytes());print(json.dumps(report,ensure_ascii=False))
