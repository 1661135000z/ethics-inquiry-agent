"""Public appearance-only payload and local theme switching contracts."""
from pathlib import Path
import shutil,subprocess,unittest
from unittest.mock import Mock,patch
from inquiry.components import render_theme,_ASSETS

class ThemeTests(unittest.TestCase):
    def test_component_only_receives_a_known_preference_and_language(self):
        renderer=Mock();callback=Mock()
        with patch('inquiry.components._component',return_value=renderer):
            render_theme({'api_key':'never-forward'},True,callback)
        self.assertEqual(renderer.call_args.kwargs['data'],{'mode':'','zh':True})
        self.assertIs(renderer.call_args.kwargs['on_change_change'],callback)
        callback.assert_not_called()
    def test_actual_asset_retains_choice_without_duplicate_initialization_events(self):
        node=shutil.which('node');bundled=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
        node=node or (str(bundled) if bundled.is_file() else None)
        if not node:self.skipTest('Node required for local DOM contract')
        script=r'''
import assert from 'node:assert/strict';import fs from 'node:fs';
class El{constructor(tag){this.tag=tag;this.children=[];this.dataset={};this.attrs={}}append(...els){this.children.push(...els)}setAttribute(k,v){this.attrs[k]=v}querySelectorAll(){return this.children.filter(c=>c.tag==='button')}}
const storage=new Map(),events=[];const root=new El('div');
global.document={documentElement:{dataset:{}},createElement:t=>new El(t),createElementNS:(ns,t)=>new El(t)};
global.localStorage={getItem(k){assert.equal(k,'inquire.appearance');return storage.get(k)},setItem(k,v){assert.equal(k,'inquire.appearance');assert.ok(['light','dark'].includes(v));storage.set(k,v)}};
global.window={matchMedia:()=>({matches:true})};
const source=fs.readFileSync(process.argv[1],'utf8');const render=(await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'))).default;
const paint=mode=>render({parentElement:{querySelector:()=>root},data:{mode,zh:false},setTriggerValue:(k,v)=>events.push([k,v])});
paint('');assert.equal(document.documentElement.dataset.inquireTheme,'dark');assert.deepEqual(events,[['change','dark']]);
paint('dark');paint('dark');assert.equal(events.length,1);assert.equal(root.children.length,2);
root.children[0].onclick();assert.equal(document.documentElement.dataset.inquireTheme,'light');assert.equal(storage.get('inquire.appearance'),'light');
paint('light');assert.equal(events.length,2);assert.equal(root.children[0].attrs['aria-pressed'],'true');
root.children=[];paint('light');assert.equal(root.children.length,2,'replacing component markup must restore the controls without a new event');assert.equal(events.length,2);
'''
        r=subprocess.run([node,'--input-type=module','-e',script,str(_ASSETS/'theme_switch.js')],capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stderr)
