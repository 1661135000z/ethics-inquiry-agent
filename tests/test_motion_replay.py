"""Execute the actual navigation asset against a minimal DOM host."""
import json
from pathlib import Path
import shutil
import subprocess
import unittest
from inquiry.components import _ASSETS

class MotionReplayTests(unittest.TestCase):
    def test_recreated_scroll_component_does_not_reopen_or_repeat_old_navigation(self):
        node=shutil.which('node')
        bundled=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
        node=node or (str(bundled) if bundled.is_file() else None)
        if not node:self.skipTest('Node required for browser contract')
        script=r'''
import assert from 'node:assert/strict';
import fs from 'node:fs';
let scrolls=0,opens=0;
const target={scrollIntoView(){scrolls++},setAttribute(){},focus(){},querySelector(){return {getAttribute(){return 'false'},click(){opens++},focus(){}}}};
global.document={querySelector(){return target}};
global.window={matchMedia(){return {matches:true}}};
global.requestAnimationFrame=fn=>fn();
const source=fs.readFileSync(process.argv[1],'utf8');
const render=(await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'))).default;
function renderFresh(nonce){render({parentElement:{querySelector(){return {}}},data:{target:'model',nonce}})}
renderFresh(1);renderFresh(1);
assert.equal(scrolls,1,'old navigation must not replay after remount');
assert.equal(opens,0,'navigation must never programmatically toggle an unrelated popup');
renderFresh(2);assert.equal(scrolls,2);
'''
        result=subprocess.run([node,'--input-type=module','-e',script,str(_ASSETS/'scroll_bridge.js')],text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)

    def test_skipping_before_handoff_prevents_a_second_transition_and_reruns_do_not_replay(self):
        node=shutil.which('node')
        bundled=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
        node=node or (str(bundled) if bundled.is_file() else None)
        if not node:self.skipTest('Node required for browser contract')
        script=r'''
import assert from 'node:assert/strict';import fs from 'node:fs';
let reduced=false;
class El{constructor(){this.style={};this.children=[];this.dataset={};this.isConnected=true}append(...x){x.forEach(e=>{e.parent=this;this.children.push(e)})}setAttribute(){}animate(){return {cancel(){}}}remove(){this.parent.children=this.parent.children.filter(e=>e!==this)}getBoundingClientRect(){return {left:20,top:70,width:270,height:36}}}
global.window={innerWidth:1366,innerHeight:768,matchMedia(){return {matches:reduced}}};
global.getComputedStyle=()=>({getPropertyValue(){return ''},backgroundColor:'#fff'});
global.document={body:new El(),documentElement:new El(),createElement(){return new El()},createElementNS(){return new El()},addEventListener(){},removeEventListener(){}};
const source=fs.readFileSync(process.argv[1],'utf8')+'\nexport {getMotionRuntime}';
const mod=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
const runtime=mod.getMotionRuntime(),target=new El();
const pending=runtime.begin({title:'Gemini',kind:'model'});assert.equal(document.body.children.length,1);
pending.layer.children.at(-1).onclick();assert.equal(document.body.children.length,0);
runtime.settle({nonce:1,kind:'model',target});assert.equal(document.body.children.length,0,'skip before Python handoff must remain skipped');
runtime.settle({nonce:1,kind:'model',target});assert.equal(document.body.children.length,0,'rerun must not replay');
reduced=true;runtime.settle({nonce:2,kind:'conversation',target});assert.equal(document.body.children.length,0);
assert.ok(runtime.seen.has(2));runtime.finish();
'''
        result=subprocess.run([node,'--input-type=module','-e',script,str(_ASSETS/'motion_runtime.js')],text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)

    def test_journey_restores_nodes_when_component_markup_is_replaced(self):
        node=shutil.which('node');bundled=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
        node=node or (str(bundled) if bundled.is_file() else None)
        if not node:self.skipTest('Node required for local DOM contract')
        script=r'''
import assert from 'node:assert/strict';import fs from 'node:fs';
class El{constructor(){this.children=[];this.dataset={};this.style={setProperty(){}}}append(...x){this.children.push(...x)}replaceChildren(...x){this.children=x}setAttribute(){}removeAttribute(){}querySelector(cls){return this.children.find(e=>'.'+e.className===cls)}}
const root=new El();global.document={createElement:()=>new El()};global.window={matchMedia:()=>({matches:true})};
const source=fs.readFileSync(process.argv[1],'utf8');const render=(await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'))).default;
const frame={parentElement:{querySelector:()=>root},data:{steps:[{id:'model',title:'Model',state:'complete',detail:'Gemini'}],current:'model'},setTriggerValue(){}};
render(frame);assert.equal(root.children.length,1);root.children=[];render(frame);assert.equal(root.children.length,1,'journey must recreate detached nodes after a host update');
'''
        r=subprocess.run([node,'--input-type=module','-e',script,str(_ASSETS/'journey.js')],capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stderr)
