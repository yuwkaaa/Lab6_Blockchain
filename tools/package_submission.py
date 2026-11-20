#!/usr/bin/env python3
"""Collect student-owned evidence into an LMS ZIP; no keys, venv or teacher files."""
import json
import zipfile
import subprocess
import sys
from pathlib import Path

base=Path('.')
identity=base/'lab_identity.json'
if not identity.exists():sys.exit('Chua co lab_identity.json: chay create_lab.py truoc.')
info=json.loads(identity.read_text(encoding='utf8'))
required=[base/'AuditTarget.sol',base/'report/MAU_BAO_CAO.md',
          base/'evidence/before_raw/slither.json',base/'evidence/before_configured/slither.json',
          base/'evidence/after_raw/slither.json',base/'evidence/after_configured/slither.json',
          base/'evidence/architecture/human_summary.txt',base/'.github/workflows/slither.yml']
missing=[str(f) for f in required if not f.exists()]
if missing:
    print('CHUA DU MINH CHUNG (khong tao ZIP):')
    for f in missing: print(' -',f)
    sys.exit(2)
files=[base/'AuditTarget.sol',base/'lab_identity.json',base/'slither.config.json',
       base/'report/MAU_BAO_CAO.md',base/'.github/workflows/slither.yml',
       base/'contracts/ArchitectureDemo.sol']
files += [p for p in (base/'evidence').rglob('*') if p.is_file()]
files=sorted(set(files),key=lambda p:str(p))
(base/'submissions').mkdir(exist_ok=True)
out=base/'submissions'/('NT547_Lab06_'+info['mssv']+'.zip')
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for p in files: z.write(p,p.as_posix())
    try:
        log=subprocess.check_output(['git','log','--format=%h %H %s','-n','10'],text=True,stderr=subprocess.DEVNULL)
        z.writestr('git_history.txt',log)
    except Exception:
        z.writestr('git_history.txt','Git history not available; supply GitHub URL/SHA in report.\n')
print('DONE:',out,'|',len(files),'files')
print('NHAC: Dien day du URL+SHA trong report; ZIP khong tu xac minh GitHub runs.')
