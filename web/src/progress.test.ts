import {it,expect} from 'vitest';
import {blankAnalysis,cleanAnalysis,dimensionView} from './analysis';
import {readinessForAnalysis} from './progress';
import {emptySnapshot,initialState,publicSnapshot,restoreState} from './state';
it('credits an unknown facet as explored while keeping its information insufficient',()=>{
 const a=blankAnalysis();a.engagements=[{id:'e1',area:'review',facet:'reviewer',quote:'不知道',turn:2,state:'unknown'}];
 const s=emptySnapshot();s.session.analysis=a;const d=dimensionView(s,'review');expect(d.coverage).toBe(1);expect(d.information).toBe(0);expect(readinessForAnalysis(a).eligible).toBe(false);
});
it('restores short source-linked engagement without accepting secret or forged source fields',()=>{
 const messages=[{role:'user' as const,content:'不知道'},{role:'assistant' as const,content:'We can explore another angle.'}];const a={...blankAnalysis(),engagements:[{id:'e1',area:'review',facet:'reviewer',quote:'不知道',turn:1,state:'unknown',api_key:'not-for-storage'},{id:'e2',area:'pressure',facet:'incentive',quote:'invented threat',turn:1,state:'position'}]};
 const clean=cleanAnalysis(a,messages)!;expect(clean.engagements).toHaveLength(1);expect(JSON.stringify(clean)).not.toContain('not-for-storage');expect(clean.readiness?.eligible).toBe(false);
});
it('retains twenty accepted turns through refresh and permits a 20-turn free budget',()=>{
 const s=initialState();s.screen='chat';s.onboarded=true;s.snapshot.session.messages=Array.from({length:40},(_,i)=>({role:i%2?'assistant' as const:'user' as const,content:'Fictional statement '+i}));s.snapshot.session.records=Array.from({length:20},(_,i)=>({turn:i+1,provider:'gemini',model:s.model,focus:'review',time:'2026-10-16T00:00:00Z'}));
 expect(restoreState(JSON.stringify(publicSnapshot(s))).snapshot.session.messages).toHaveLength(40);
});
import fixtures from './progress-fixtures.json';
import {dimensionState} from './progress';
import type {Analysis} from './analysis';
it('matches the Python source-of-truth for exploration, sufficiency and readiness',()=>{
 for(const fixture of fixtures){const a=fixture as unknown as Analysis;for(const [area,expected] of Object.entries(fixture.dimensions)){const d=dimensionState(a,area);expect(d.coverage).toBe(expected.coverage);expect(d.information).toBe(expected.information);expect(d.declined).toEqual(expected.declined)}expect(readinessForAnalysis(a)).toEqual(fixture.readiness)}
});
