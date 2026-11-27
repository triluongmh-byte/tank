#!/usr/bin/env python3
"""Host-only checks; all available CPUs, incremental per executable and result."""
import concurrent.futures,hashlib,json,os,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parent.parent
FIRM=ROOT/'firmware';OUT=ROOT/'build/firmware/tests';OUT.mkdir(parents=True,exist_ok=True)
jobs=os.cpu_count() or 1
headers=sorted((FIRM/'tank').glob('*.h'))
def digest(paths):
 h=hashlib.sha256()
 for p in paths:h.update(str(p.relative_to(ROOT)).encode());h.update(p.read_bytes())
 return h.hexdigest()
def run_test(name,extra):
 source=FIRM/'tests'/f'{name}.cpp';binary=OUT/name;stamp=OUT/f'{name}.sha256'
 inputs=[source,*headers,*sorted((FIRM/'tests/mock').glob('*'))]
 if name=='scan_test':
  fixture=OUT/'scan-fixture';fixture.mkdir(exist_ok=True)
  for filename in ('controller.h','pins.h'):(fixture/filename).write_bytes((FIRM/'tank'/filename).read_bytes())
  (fixture/'mechanical_limits.h').write_text('#pragma once\nnamespace tank { constexpr int CASE_YAW_MIN=-30, CASE_YAW_MAX=30; }\n')
  extra=['-I',str(fixture),*extra]
 sha=digest(inputs)
 if not binary.exists() or not stamp.exists() or stamp.read_text()!=sha:
  subprocess.run(['clang++','-std=c++17','-O1','-g','-fsanitize=address,undefined','-Wall','-Wextra','-Werror','-Wno-misleading-indentation',*extra,'-I',str(FIRM/'tank'),str(source),'-o',str(binary)],check=True,cwd=ROOT)
  stamp.write_text(sha)
 result=OUT/f'{name}.passed'
 if result.exists() and result.read_text()==sha:print('UNCHANGED',name);return
 subprocess.run([str(binary)],check=True,cwd=ROOT);result.write_text(sha)
selected=sys.argv[1:] or ['core','guard','pet','scan','host','interfaces']
with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:
 futures=[]
 for group in selected:
  if group in ('core','guard','pet','scan'):
   futures.append(pool.submit(run_test,group+'_test',['-I',str(FIRM/'tests/mock')] if group=='guard' else []))
  elif group=='host':futures.append(pool.submit(subprocess.run,[sys.executable,'-B','-m','unittest','discover','-s',str(FIRM/'tests'),'-p','test_*.py'],check=True,cwd=ROOT))
  elif group=='interfaces':futures.append(pool.submit(subprocess.run,[sys.executable,str(FIRM/'reconcile.py')],check=True,cwd=ROOT))
  else:raise SystemExit('Unknown check '+group)
 for f in futures:f.result()
print('PASS requested firmware checks (hardware untested)')
