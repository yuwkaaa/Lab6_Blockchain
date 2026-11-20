#!/usr/bin/env python3
"""Print architecture for provided demo; output in evidence/architecture."""
import pathlib,subprocess,shutil,sys
p=pathlib.Path('evidence/architecture');p.mkdir(parents=True,exist_ok=True)
target='contracts/ArchitectureDemo.sol'
for opt,out in [('human-summary','human_summary.txt'),('inheritance-graph','printer_log.txt')]:
    cmd=['slither',target,'--print',opt,'--config-file','config/slither.raw.json','--fail-none']
    proc=subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (p/out).write_text(' '.join(cmd)+'\n'+proc.stdout,encoding='utf8')
    if proc.returncode!=0:
        sys.exit('Printer failed: '+str(p/out)+' ; xem log va cai dat.')
files=list(pathlib.Path('.').rglob('ArchitectureDemo.sol.dot'))
if not files:
    print('Khong tim thay *.dot. Kiem tra evidence/architecture/printer_log.txt');sys.exit(1)
for dot in files:
    dest=p/dot.name
    if dot.resolve()!=dest.resolve():shutil.copy2(dot,dest)
    if shutil.which('dot'):
        result=subprocess.run(['dot','-Tpng',str(dest),'-o',str(p/'inheritance.png')],capture_output=True,text=True)
        if result.returncode:print('Graphviz err:',result.stderr)
print('DONE: evidence/architecture / anh inheritance.png (neu co Graphviz).')
