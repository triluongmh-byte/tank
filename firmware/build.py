#!/usr/bin/env python3
"""Incremental, all-core compile only; never upload or enumerate hardware."""
import hashlib,json,os,pathlib,shutil,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parent.parent
FIRM=ROOT/'firmware'; OUT=ROOT/'build/firmware/esp32'
recipe=json.loads((FIRM/'flash.json').read_text())
cli=shutil.which('arduino-cli')
if not cli: sys.exit('arduino-cli missing; use the shared Harness toolchain')
cores=subprocess.check_output([cli,'core','list','--format','json'],text=True)
parsed=json.loads(cores)
# Arduino CLI emits platforms list in recent versions, older versions a direct list.
platforms=parsed.get('platforms',[]) if isinstance(parsed,dict) else parsed
if not any(p.get('id')=='esp32:esp32' and p.get('installed_version',p.get('installed',''))=='2.0.14' for p in platforms):
 sys.exit('Requires installed shared esp32:esp32@2.0.14; do not install inside this worktree')
h=hashlib.sha256((recipe['fqbn']+'esp32:esp32@2.0.14'+os.environ.get('ARDUINO_DIRECTORIES_DATA','')).encode())
for p in sorted((FIRM/'tank').glob('*')):
 if p.is_file():h.update(p.name.encode());h.update(p.read_bytes())
fingerprint=h.hexdigest();stamp=OUT/'inputs.sha256';binary=OUT/'tank.ino.bin'
if stamp.exists() and stamp.read_text().strip()==fingerprint and binary.exists():
 print('Firmware sources unchanged: reusing',binary);sys.exit(0)
OUT.mkdir(parents=True,exist_ok=True)
cmd=[cli,'compile','--fqbn',recipe['fqbn'],'--jobs',str(os.cpu_count() or 1),'--build-path',str(OUT),str(FIRM/'tank')]
subprocess.run(cmd,cwd=ROOT,check=True)
if not binary.exists():sys.exit('Compiler returned without expected binary')
stamp.write_text(fingerprint+'\n')
(OUT/'build-evidence.json').write_text(json.dumps({'command':cmd,'core':'esp32:esp32@2.0.14','contractSha256':'a3ef67fc11d668fdbe01fd2d5a06c6fef5fed069868d7fb6fb4b3995edd55810','inputSha256':fingerprint,'binarySha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'hardwareTested':False},indent=2)+'\n')
