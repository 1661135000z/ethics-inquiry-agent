import {it,expect} from 'vitest';
import {renderToStaticMarkup} from 'react-dom/server';
import {ReviewPreview} from './ExperiencePanels';
import {initialState} from './state';
it('retains static source attribution when interactive links are hidden for printing',()=>{
 const snapshot=initialState().snapshot;snapshot.initial_text='Fictional input';snapshot.session.messages=[{role:'user',content:'I do not know whether the data are complete.'},{role:'assistant',content:'Who can verify that?'}];snapshot.session.observations=[{area:'evidence',quote:'I do not know whether the data are complete.'}];
 const html=renderToStaticMarkup(<ReviewPreview snapshot={snapshot} zh={false} onLocate={()=>{}}/>);
 expect(html).toContain('<cite>Turn 1</cite>');expect(html).toContain('I do not know whether the data are complete.');
});
