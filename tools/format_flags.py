#!/usr/bin/env python3
"""Print evidence ID from local identity and optional Git SHAs (not grading secrets)."""
import json,subprocess
from pathlib import Path
f=Path('lab_identity.json')
if not f.exists():raise SystemExit('Chay python tools/create_lab.py MSSV truoc')
x=json.loads(f.read_text(encoding='utf8'))
print('MSSV:',x['mssv'],'| session:',x['session_code'],'| contract:',x['contract'])
try:
 sha=subprocess.check_output(['git','rev-parse','--short=7','HEAD'],text=True,stderr=subprocess.DEVNULL).strip()
 print('HEAD short SHA:',sha)
except Exception:print('Chua co commit Git.')
