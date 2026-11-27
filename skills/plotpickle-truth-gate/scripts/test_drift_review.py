import subprocess,sys,tempfile,json
from pathlib import Path
from PIL import Image
CMD=Path(__file__).with_name('drift_review.py')
def run(*a):return subprocess.run([sys.executable,str(CMD),*map(str,a)],capture_output=True,text=True)
with tempfile.TemporaryDirectory() as d:
    d=Path(d);image=d/'raw.png';watermark=d/'marked.png'
    Image.new('RGB',(640,360),'#333333').save(image)
    raw=image.read_bytes()
    good=run('stamp','--image',image,'--out',watermark,'--status','DRIFTED','--reason','wrong character identity')
    assert good.returncode==0,good.stderr
    assert image.read_bytes()==raw
    assert watermark.exists() and (d/'marked.png.receipt.json').exists()
    assert run('stamp','--image',image,'--out',d/'bad.png','--status','PASS','--reason','no').returncode!=0
    assert run('stamp','--image',image,'--out',image,'--status','DRIFTED','--reason','no').returncode!=0
    assert run('stamp','--image',image,'--out',d/'empty.png','--status','DRIFTED','--reason',' ').returncode!=0
    report={'shots':[{'productionAddress':'B02-M02-S12','semanticState':'DRIFTED','reason':'wrong actor','usableForProduction':False},{'productionAddress':'B02-M02-S11','semanticState':'UNKNOWN','usableForProduction':False}]}
    p=d/'report.json';p.write_text(json.dumps(report));assert run('gate','--review',p).returncode==0
    report['shots'][0]['usableForProduction']=True;p.write_text(json.dumps(report));assert run('gate','--review',p).returncode!=0
print('PASS: DRIFTED-only stamp, exact original preservation, review gate negative tests')
