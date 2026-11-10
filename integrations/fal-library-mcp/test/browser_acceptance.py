"""Browser widget acceptance with mocked host and fal response. Not live ChatGPT/fal integration."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json
root=Path(__file__).resolve().parents[1]
html=(root/'widget.html').read_text()
body,script=html.split('<script>',1)
script=script.split('</script>',1)[0]
clip=Path('/mnt/data/CL1nqK_1X4P4uHM1Td6kf_QYad0gXz.mp4').read_bytes()
fal='https://v3b.fal.media/files/b/0ab1d25b/CL1nqK_1X4P4uHM1Td6kf_QYad0gXz.mp4'
config={'url':fal,'expectedBytes':len(clip),'storyId':'The Third Bell','shotId':'Shot 01','filename':'browser-fixture.mp4'}
host='''(config)=>{window.__uploads=[];window.__state=null;window.openai={toolOutput:config,uploadFile:async(file,options)=>{window.__uploads.push({size:file.size,type:file.type,filename:file.name,options});return {fileId:'mock-host-file-01'};},getFileDownloadUrl:async()=>({downloadUrl:'https://mock.chatgpt.invalid/clip.mp4'}),setWidgetState:(state)=>window.__state=state};}'''
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=browser.new_page()
 page.route('https://v3b.fal.media/**',lambda r:r.fulfill(status=200,body=clip,content_type='video/mp4',headers={'access-control-allow-origin':'*','content-length':str(len(clip))}))
 page.route('https://mock.chatgpt.invalid/**',lambda r:r.fulfill(status=200,body=clip,content_type='video/mp4',headers={'access-control-allow-origin':'*'}))
 page.set_content(body)
 page.evaluate(host,config)
 # about:blank is not a secure context here; inject mock digest for browser-only acceptance.
 page.evaluate("Object.defineProperty(window.crypto, 'subtle', {configurable:true, value:{digest:async()=>new Uint8Array(32).buffer}})")
 page.add_script_tag(content=script)
 button=page.get_by_role('button',name='Save original to ChatGPT Library')
 assert button.is_enabled()
 button.click()
 page.get_by_text('Saved and byte-for-byte readback verified.',exact=False).wait_for(timeout=20000)
 uploads=page.evaluate('window.__uploads')
 assert len(uploads)==1 and uploads[0]['size']==len(clip) and uploads[0]['options']=={'library':True}
 state=page.evaluate('window.__state.privateContent')
 assert state['readback']=='verified' and len(state['sha256'])==64
 print('PASS mocked browser upload/readback',json.dumps(uploads))
 page.close()
 page=browser.new_page()
 page.set_content(body)
 page.add_script_tag(content=script)
 assert page.get_by_role('button',name='Save original to ChatGPT Library').is_disabled()
 assert 'Loading the transfer tool.' in page.locator('#status').inner_text()
 print('PASS no-host/no-source fail closed')
 browser.close()
