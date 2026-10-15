import {it,expect} from 'vitest';
import {renderToStaticMarkup} from 'react-dom/server';
import {ReviewPreview} from './ExperiencePanels';
import {initialState} from './state';
it('retains static source attribution when interactive links are hidden for printing',()=>{
 const snapshot=initialState().snapshot;snapshot.initial_text='Fictional input';snapshot.session.messages=[{role:'user',content:'I do not know whether the data are complete.'},{role:'assistant',content:'Who can verify that?'}];snapshot.session.observations=[{area:'evidence',quote:'I do not know whether the data are complete.'}];
 const html=renderToStaticMarkup(<ReviewPreview snapshot={snapshot} zh={false} onLocate={()=>{}}/>);
 expect(html).toContain('<cite>Turn 1</cite>');expect(html).toContain('I do not know whether the data are complete.');
});

it('labels the historical example as read-only and preserves the actual original question',async()=>{
 const {RecordedExample}=await import('./RecordedExample');const html=renderToStaticMarkup(<RecordedExample zh={false}/>);
 expect(html).toContain('Recorded inquiry');expect(html).toContain('read-only');expect(html).toContain('12 October 2026');expect(html).toContain('What steps can you take to verify whether the missing manual entries');expect(html).toContain('Viewing makes no model call');
});
