"""Full official board check, cached by every owned source/evidence byte. No source rebuild."""
import concurrent.futures,hashlib,json,os,pathlib,subprocess
R=pathlib.Path('.');py=os.environ['KICAD_HARNESS_PYTHON'];cache=R/'build/board/check-cache.json'
files=[p for folder in ['design','engineering','tools/board'] for p in (R/folder).rglob('*') if p.is_file() and '__pycache__' not in str(p)]+[R/p for p in ['parts.json','product.json','manufacturing.json'] if (R/p).exists()]
def digest(p):return str(p)+':'+hashlib.sha256(p.read_bytes()).hexdigest()
def key():
 with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as ex:entries=sorted(ex.map(digest,files))
 return hashlib.sha256('\n'.join(entries).encode()).hexdigest()
before=key();old=json.loads(cache.read_text()) if cache.exists() else {}
if old.get('inputSha256')!=before:
 for args in [[py,'tools/board/power-model.py'],[py,'tools/board/pack-protection.py'],[py,'tools/board/audit.py'],[py,'tools/board/review.py'],[py,'-m','kicadpy.verify','netlist','design/main.kicad_pro'],[py,'-m','kicadpy.verify','enables','design/main.kicad_pro','parts.json'],[py,'-m','kicadpy.publish','--manufacturing','design/main.kicad_pro']]:subprocess.run(args,check=True,timeout=600)
else:print('Owned inputs unchanged; reusing official publication.')
subprocess.run([py,'-m','kicadpy.verify','gate','.'],check=True,timeout=60)
subprocess.run([py,'-m','kicadpy.verify','stale','.'],check=True,timeout=60)
j=json.load(open('boards/main.board.json'));ready=j.get('fab',{}).get('ready',False)
if ready:cache.write_text(json.dumps({'inputSha256':key(),'prototypeReady':True},indent=2))
else:raise SystemExit('Board is not prototype-ready; inspect official reports.')
