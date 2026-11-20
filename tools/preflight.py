#!/usr/bin/env python3
import sys,shutil,subprocess,json
from pathlib import Path
print('Python:',sys.version.split()[0])
for name in ('git','slither','solc','dot'):
    exe=shutil.which(name);print(name, 'OK: '+exe if exe else 'CHUA CAI (xem huong dan)')
required=['tools/create_lab.py','tools/scan.py','tools/print_arch.py',
          'config/slither.raw.json','slither.config.json','.github/workflows/slither.yml',
          'contracts/ArchitectureDemo.sol']
for x in required:
    print('file',x,'OK' if Path(x).exists() else 'THIEU')
print('Tip: chay trong THU MUC 01_SINH_VIEN (thu muc chua tools/).')
