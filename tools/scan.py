#!/usr/bin/env python3
"""Run Slither and export reproducible raw/configured evidence to CSV, JSON, TXT.
Only prerequisites: slither+solc installed. The CLI's --fail-none is intentional:
a finding is NOT a process error during triage; CI determines the quality gate.
"""
import argparse,csv,json,subprocess,sys,shutil
from pathlib import Path

def run(args):
    p=subprocess.run(args,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    return p.returncode,p.stdout

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--mode',choices=('raw','configured'),required=True)
    ap.add_argument('--tag',required=True,help='VD: before, after, mutation')
    ap.add_argument('--target',default='AuditTarget.sol')
    a=ap.parse_args()
    if not shutil.which('slither'):
        sys.exit('Khong tim thay slither. Xem 01_HUONG_DAN_LAB06.docx muc Cai dat.')
    if not shutil.which('solc'):
        sys.exit('Khong tim thay solc. Chay: solc-select install 0.8.24 && solc-select use 0.8.24')
    target=Path(a.target)
    if not target.exists():sys.exit('Khong tim thay '+str(target)+'; chay tools/create_lab.py <MSSV> truoc.')
    evidence=Path('evidence')/(a.tag+'_'+a.mode)
    evidence.mkdir(parents=True,exist_ok=True)
    raw=evidence/'slither.json'
    cfg= 'config/slither.raw.json' if a.mode=='raw' else 'slither.config.json'
    cmd=['slither',str(target),'--config-file',cfg,'--fail-none','--json',str(raw)]
    rc,out=run(cmd)
    slc,solc_ver=run(['solc','--version']); slv,slither_ver=run(['slither','--version'])
    (evidence/'command_and_output.txt').write_text(
      'COMMAND: '+ ' '.join(cmd)+'\n'+ 'SLITHER_VERSION:\n'+slither_ver+
      '\nSOLC_VERSION:\n'+solc_ver+'\n'+out,encoding='utf8')
    if not raw.exists():
      sys.exit('Chua co JSON (Slither exit='+str(rc)+'). Xem '+str(evidence/'command_and_output.txt'))
    try:doc=json.loads(raw.read_text(encoding='utf8'))
    except Exception as exc:sys.exit('JSON khong hop le: '+str(exc))
    if not doc.get('success',False):
      sys.exit('Slither JSON success=false. Xem '+str(evidence/'command_and_output.txt'))
    issues=doc.get('results',{}).get('detectors',[]) or []
    cnt={k:0 for k in ('High','Medium','Low','Informational','Optimization','Other')}
    headers=('index','check','impact','confidence','file','lines','description')
    with (evidence/'findings.csv').open('w',newline='',encoding='utf-8-sig') as f:
      writer=csv.writer(f);writer.writerow(headers)
      for i,d in enumerate(issues,1):
        severity=d.get('impact','Other');cnt[severity if severity in cnt else 'Other']+=1
        places=[]
        for e in d.get('elements',[]):
          src=e.get('source_mapping') or {}
          places.append((src.get('filename_relative') or src.get('filename_short') or '',
                         ','.join(map(str,src.get('lines') or []))))
        names='; '.join(sorted(set(x for x,_ in places if x)))
        ln='; '.join(sorted(set(y for _,y in places if y)))
        writer.writerow([i,d.get('check',''),severity,d.get('confidence',''),names,ln,
                         (d.get('description','') or '').replace('\n',' ').strip()])
    summary={'mode':a.mode,'tag':a.tag,'count':cnt,'total':len(issues),'solc':solc_ver.strip(),
             'command':' '.join(cmd),'process_exit_code':rc}
    (evidence/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    print('DONE:',evidence, '| issues=',len(issues),'|',cnt)
    print('Nop: slither.json, findings.csv, summary.json, command_and_output.txt')
if __name__=='__main__':main()
